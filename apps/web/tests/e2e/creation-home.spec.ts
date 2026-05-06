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

const creativeModelCases = [
  {
    id: "deepseek",
    label: "DeepSeek",
    provider: "deepseek",
    model: "deepseek-chat",
  },
  {
    id: "mimo",
    label: "Mimo",
    provider: "mimo",
    model: "mimo-v2.5-pro",
  },
  {
    id: "kimi",
    label: "Kimi",
    provider: "kimi",
    model: "kimi-k2.5",
  },
  {
    id: "minimax",
    label: "MiniMax",
    provider: "minimax",
    model: "MiniMax-M2.7",
  },
];

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

type RequestContextOptions = {
  user_id?: string;
  workspace_id?: string;
  project_id?: string;
  session_id?: string;
  request_id?: string;
  source_stage?: string;
  context_policy?: string;
};

type ScriptGenerationPayload = {
  source_mode?: string;
  ai_options?: {
    provider?: string;
    model?: string;
  };
  context_options?: RequestContextOptions;
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

async function fillIdeaDraftAndGenerate(page: Page, projectTitle: string) {
  await page.getByTestId("creation-entry-card-idea").click();
  await page.getByLabel("项目标题").fill(projectTitle);
  await page.getByLabel("类型 / 风格").fill("都市悬疑");
  await page.getByLabel("目标集数").fill("1");
  await page.getByLabel("灵感内容").fill("一名编剧回到旧楼，发现未完成的剧本正在改写现实。");
  await page.getByLabel("额外要求").fill("对白自然，每集结尾有强钩子。");
  await page.getByTestId("generate-short-drama-script").click();
}

async function fillAdaptationDraftAndGenerate(
  page: Page,
  mode: "film" | "novel",
  projectTitle: string,
) {
  await page.getByTestId("creation-entry-card-adaptation").click();
  await page.getByTestId(mode === "film" ? "creation-entry-card-film" : "creation-entry-card-novel").click();
  await page.getByLabel("项目标题").fill(projectTitle);
  await page
    .getByLabel(mode === "film" ? "原片 / 原剧本标题" : "原小说 / 文本标题")
    .fill(mode === "film" ? "旧影院来信" : "雨巷旧梦");
  await page.getByLabel("目标集数").fill("3");
  await page
    .getByLabel(mode === "film" ? "原剧本 / 长文本内容" : "小说 / 网文 / 故事文本")
    .fill(
      mode === "film"
        ? "一座即将停业的旧影院里，放映员收到一封写给未来的信。"
        : "雨巷尽头的修伞铺里，年轻人发现一张从未寄出的旧船票。",
    );
  await page.getByLabel("改编方向 / 重点要求").fill("改成三集短剧，保留主冲突，每集结尾有反转。");
  await page.getByLabel("额外要求").fill("对白自然，节奏紧凑。");
  await page.getByRole("button", { name: "生成改编短剧本" }).click();
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
    await expect(page.getByRole("button", { name: /DeepSeek/ })).toBeVisible();
    await expect(page.getByRole("button", { name: /Mimo/ })).toBeVisible();
    await expect(page.getByRole("button", { name: /Kimi/ })).toBeVisible();
    await expect(page.getByRole("button", { name: /MiniMax/ })).toBeVisible();
    await expect(page.getByText("系统默认模型")).toHaveCount(0);
    await expect(page.getByText("使用后端默认", { exact: false })).toHaveCount(0);
  });

  test("submits selected creative model provider and model in generation request", async ({ page }) => {
    const capturedPayloads = new Map<string, ScriptGenerationPayload>();
    let activeModelId = "";

    await page.route("**/api/scripts/generate-from-source", async (route) => {
      capturedPayloads.set(activeModelId, route.request().postDataJSON() as ScriptGenerationPayload);
      await route.fulfill({
        contentType: "application/json",
        status: 200,
        body: JSON.stringify(generatedScriptFixture),
      });
    });

    for (const modelCase of creativeModelCases) {
      await test.step(`submits ${modelCase.label}`, async () => {
        activeModelId = modelCase.id;
        await page.goto("/");
        await login(page);

        await page.getByRole("button", { name: "切换" }).click();
        await page.getByTestId(`creative-model-option-${modelCase.id}`).click();
        await expect(page.getByText(`创作模型：${modelCase.label}`)).toBeVisible();

        await fillIdeaDraftAndGenerate(page, `模型切换测试：${modelCase.label}`);
        await expect(page.getByTestId("short-drama-script-result")).toBeVisible();

        const payload = capturedPayloads.get(modelCase.id);
        expect(payload?.ai_options?.provider).toBe(modelCase.provider);
        expect(payload?.ai_options?.model).toBe(modelCase.model);
        expect(payload?.context_options?.context_policy).toBe("current_project_only");
        expect(payload?.context_options?.source_stage).toBe("generated_script");
      });
    }
  });

  test("submits context options for all script creation entries", async ({ page }) => {
    const capturedPayloads = new Map<string, ScriptGenerationPayload>();

    await page.route("**/api/scripts/generate-from-source", async (route) => {
      const payload = route.request().postDataJSON() as ScriptGenerationPayload;
      if (payload.source_mode) {
        capturedPayloads.set(payload.source_mode, payload);
      }

      await route.fulfill({
        contentType: "application/json",
        status: 200,
        body: JSON.stringify({
          ...generatedScriptFixture,
          source_mode: payload.source_mode ?? generatedScriptFixture.source_mode,
        }),
      });
    });

    await page.goto("/");
    await login(page);

    await fillIdeaDraftAndGenerate(page, "上下文验收：灵感入口");
    await expect(page.getByTestId("short-drama-script-result")).toBeVisible();

    await page.goto("/");
    await login(page);
    await fillAdaptationDraftAndGenerate(page, "film", "上下文验收：电影入口");
    await expect(page.getByTestId("short-drama-script-result")).toBeVisible();

    await page.goto("/");
    await login(page);
    await fillAdaptationDraftAndGenerate(page, "novel", "上下文验收：小说入口");
    await expect(page.getByTestId("short-drama-script-result")).toBeVisible();

    expect(capturedPayloads.get("idea")?.context_options?.context_policy).toBe(
      "current_project_only",
    );
    expect(capturedPayloads.get("film_script")?.context_options?.project_id).toBe(
      "project_creation_default",
    );
    expect(capturedPayloads.get("novel")?.context_options?.session_id).toBe(
      "session_creation_default",
    );

    for (const payload of capturedPayloads.values()) {
      expect(payload.context_options?.workspace_id).toBe("workspace_dramora_internal");
      expect(payload.context_options?.request_id).toMatch(/^request_\d+$/);
    }
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

});
