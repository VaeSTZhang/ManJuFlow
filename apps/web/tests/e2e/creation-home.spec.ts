import { readFile } from "node:fs/promises";
import { expect, test, type Page } from "@playwright/test";

const blockedUiPhrases = [
  "后端 mock",
  "本地后端",
  "本地演示",
  "使用后端默认",
  "MVP",
  "第五阶段",
];

const originalScriptTitle = "测试短剧：旧楼灯火";
const originalScriptLogline = "一名年轻编剧回到旧楼，发现每盏灯都藏着一段未完成的短剧真相。";
const originalWorldSetting = "当代都市，旧楼改造前夜。";
const editedScriptTitle = "测试短剧：灯火归来";
const editedScriptLogline = "年轻编剧回到旧楼，在层层反转中找回父亲留下的最后一场戏。";
const editedWorldSetting = "当代都市旧楼即将拆迁，所有角色都被一份未完成剧本重新牵连。";

const generatedScriptFixture = {
  project_title: originalScriptTitle,
  source_mode: "idea",
  logline: originalScriptLogline,
  world_setting: originalWorldSetting,
  characters: [
    {
      name: "林乔",
      role: "主角",
      age: "28",
      personality: "敏锐、克制、执着",
      arc: "从逃避旧事到主动揭开真相。",
    },
    {
      name: "周闻",
      role: "对手",
      age: "35",
      personality: "圆滑、强势、谨慎",
      arc: "从掌控局面到被迫面对过往。",
    },
  ],
  adaptation_notes: null,
  episode_count: 1,
  episodes: [
    {
      episode_number: 1,
      title: "旧楼来电",
      summary: "林乔收到旧楼管理处电话，被迫回到三年前离开的地方。",
      hook: "她在父亲旧桌里发现一份写着自己名字的剧本。",
      scenes: [
        {
          scene_number: 1,
          location: "旧楼走廊",
          time: "夜",
          description: "停电后的走廊里，只有尽头办公室亮着灯。",
          dialogues: [
            {
              character: "林乔",
              line: "这栋楼不是早就没人了吗？",
            },
            {
              character: "周闻",
              line: "有些事，不是没人就能消失。",
            },
          ],
          visual_notes: "冷色灯光，长走廊压迫感。",
          emotion_curve: "疑惑到紧张。",
        },
      ],
    },
  ],
  metadata: {
    generation_mode: "llm",
    provider: "deepseek",
    model: "deepseek-chat",
    purpose: "script_generation",
  },
};

async function login(page: Page) {
  await page.getByRole("button", { name: "登录" }).click();
  await expect(page.getByRole("button", { name: "退出登录" })).toBeVisible();
}

async function mockScriptGeneration(page: Page) {
  await page.route("**/api/scripts/generate-from-source", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      status: 200,
      body: JSON.stringify(generatedScriptFixture),
    });
  });
}

async function generateIdeaScript(page: Page) {
  await page.goto("/");
  await login(page);

  await page.getByTestId("creation-entry-card-idea").click();
  await page.getByLabel("项目标题").fill(originalScriptTitle);
  await page.getByLabel("类型 / 风格").fill("都市悬疑");
  await page.getByLabel("目标集数").fill("1");
  await page.getByLabel("灵感内容").fill(originalScriptLogline);
  await page.getByLabel("额外要求").fill("对白自然，每集结尾有强钩子。");
  await page.getByTestId("generate-short-drama-script").click();

  await expect(page.getByTestId("short-drama-script-result")).toBeVisible();
  await expect(page.getByRole("heading", { name: originalScriptTitle })).toBeVisible();
}

async function editGeneratedScriptBasicFields(page: Page) {
  await page.getByTestId("start-script-editing").click();
  await page.getByTestId("script-title-editor").fill(editedScriptTitle);
  await page.getByTestId("script-logline-editor").fill(editedScriptLogline);
  await page.getByTestId("script-world-setting-editor").fill(editedWorldSetting);
  await page.getByTestId("save-script-editing").click();
}

test.describe("Dramora creation home smoke", () => {
  test("renders the creation home without visible development phrases", async ({ page }) => {
    await page.goto("/");

    await expect(page.getByTestId("creation-home")).toBeVisible();
    await expect(page.getByRole("heading", { name: "Dramora｜剧作工坊" })).toBeVisible();
    await expect(page.getByText("短剧剧本生成与改编工作台").first()).toBeVisible();

    for (const phrase of blockedUiPhrases) {
      await expect(page.getByText(phrase, { exact: false })).toHaveCount(0);
    }
  });

  test("shows the three script creation entries after selecting adaptation", async ({ page }) => {
    await page.goto("/");
    await login(page);

    await expect(page.getByTestId("creation-entry-card-idea")).toContainText("灵感生成短剧剧本");
    await page.getByTestId("creation-entry-card-adaptation").click();

    await expect(page.getByTestId("creation-entry-card-film")).toContainText("电影剧本改编");
    await expect(page.getByTestId("creation-entry-card-novel")).toContainText("小说 / 网文改编");
  });

  test("uses product wording for creative model selection", async ({ page }) => {
    await page.goto("/");
    await login(page);

    await expect(page.getByText("创作模型：DeepSeek")).toBeVisible();
    await page.getByRole("button", { name: "切换" }).click();
    await expect(page.getByText("系统默认模型")).toBeVisible();
    await expect(page.getByText("沿用当前系统配置的创作模型。")).toBeVisible();
    await expect(page.getByText("使用后端默认", { exact: false })).toHaveCount(0);
  });

  test("shows document import preview controls for the film adaptation entry", async ({ page }) => {
    await page.goto("/");
    await login(page);

    await page.getByTestId("creation-entry-card-adaptation").click();
    await page.getByTestId("creation-entry-card-film").click();

    await expect(page.getByText("电影剧本改编短剧本")).toBeVisible();
    await expect(page.getByTestId("document-import-panel")).toBeVisible();
    await expect(page.getByText("导入剧本文档内容")).toBeVisible();
    await expect(page.getByRole("button", { name: "生成导入预览" })).toBeVisible();
    await expect(page.getByText(/mock|本地后端|后端 mock/i)).toHaveCount(0);
  });

  test("does not show document import controls for the idea entry", async ({ page }) => {
    await page.goto("/");
    await login(page);

    await page.getByTestId("creation-entry-card-idea").click();

    await expect(page.getByText("灵感生成短剧剧本")).toBeVisible();
    await expect(page.getByTestId("document-import-panel")).toHaveCount(0);
    await expect(page.getByText("导入剧本文档内容")).toHaveCount(0);
  });

  test("allows editing basic generated script fields", async ({ page }) => {
    await mockScriptGeneration(page);
    await generateIdeaScript(page);
    await editGeneratedScriptBasicFields(page);

    await expect(page.getByRole("heading", { name: editedScriptTitle })).toBeVisible();
    await expect(page.getByText(editedScriptLogline)).toBeVisible();
    await expect(page.getByText(editedWorldSetting)).toBeVisible();
    await expect(page.getByText("当前展示：编辑稿")).toBeVisible();

    for (const phrase of blockedUiPhrases) {
      await expect(page.getByText(phrase, { exact: false })).toHaveCount(0);
    }
  });

  test("uses edited script content for copy and text download", async ({ page, context }) => {
    await context.grantPermissions(["clipboard-read", "clipboard-write"]);
    await mockScriptGeneration(page);
    await generateIdeaScript(page);
    await editGeneratedScriptBasicFields(page);

    await page.getByTestId("copy-script-json").click();
    const clipboardText = await page.evaluate(() => navigator.clipboard.readText());
    const copiedScript = JSON.parse(clipboardText) as {
      project_title: string;
      logline: string;
      world_setting: string;
    };

    expect(copiedScript.project_title).toBe(editedScriptTitle);
    expect(copiedScript.logline).toBe(editedScriptLogline);
    expect(copiedScript.world_setting).toBe(editedWorldSetting);
    expect(copiedScript.project_title).not.toBe(originalScriptTitle);
    expect(copiedScript.logline).not.toBe(originalScriptLogline);
    expect(copiedScript.world_setting).not.toBe(originalWorldSetting);

    const downloadPromise = page.waitForEvent("download");
    await page.getByTestId("download-script-txt").click();
    const download = await downloadPromise;
    const downloadPath = await download.path();

    expect(downloadPath).not.toBeNull();
    const downloadedText = await readFile(downloadPath as string, "utf-8");

    expect(downloadedText).toContain(editedScriptTitle);
    expect(downloadedText).toContain(editedScriptLogline);
    expect(downloadedText).toContain(editedWorldSetting);
  });
});
