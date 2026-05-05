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
const editedCharacterName = "林灯";
const editedCharacterPersonality = "冷静、敏锐，习惯用剧本逻辑拆解现实冲突。";
const editedCharacterArc = "从逃避旧楼真相，到主动完成父亲留下的最后一场戏。";
const editedEpisodeTitle = "灯火重启";
const editedEpisodeSummary = "林灯回到旧楼后，发现父亲留下的剧本与拆迁名单同时指向同一个秘密。";
const editedEpisodeHook = "她翻到最后一页，发现下一场戏的主角写着自己的名字。";

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

type DocumentExportPayload = {
  project_title: string;
  document_type?: string;
  source_stage?: string;
  content_text?: string | null;
  structured_payload?: Record<string, any> | null;
  export_format: "txt" | "json" | "docx";
  filename?: string | null;
  context_options?: RequestContextOptions;
  metadata?: Record<string, unknown>;
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

type DocumentImportPayload = {
  filename: string;
  extracted_text: string;
  source_type?: string;
  project_title?: string | null;
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

async function mockDocumentExport(page: Page, capturedPayloads: DocumentExportPayload[] = []) {
  await page.route("**/api/documents/export", async (route) => {
    const payload = route.request().postDataJSON() as DocumentExportPayload;
    capturedPayloads.push(payload);

    const contentText =
      payload.export_format === "json"
        ? JSON.stringify(payload.structured_payload ?? {}, null, 2)
        : payload.content_text ?? "";

    await route.fulfill({
      contentType: "application/json",
      status: 200,
      body: JSON.stringify({
        project_title: payload.project_title,
        document_type: payload.document_type ?? "short_drama_script",
        source_stage: payload.source_stage ?? "script",
        export_format: payload.export_format,
        filename:
          payload.filename ??
          `dramora-short-drama-script.${payload.export_format}`,
        content_text: contentText,
        download_url: null,
        file_size_bytes: new TextEncoder().encode(contentText).length,
        metadata: payload.metadata ?? {},
      }),
    });
  });
}

async function mockDocumentExportFile(page: Page, capturedPayloads: DocumentExportPayload[] = []) {
  await page.route("**/api/documents/export-file", async (route) => {
    const payload = route.request().postDataJSON() as DocumentExportPayload;
    capturedPayloads.push(payload);

    await route.fulfill({
      contentType: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      status: 200,
      headers: {
        "Content-Disposition": 'attachment; filename="dramora-short-drama-script.docx"',
      },
      body: Buffer.from("safe fake docx bytes for e2e"),
    });
  });
}

async function mockDocumentImportPreview(page: Page, capturedPayloads: DocumentImportPayload[] = []) {
  await page.route("**/api/documents/import-preview", async (route) => {
    const payload = route.request().postDataJSON() as DocumentImportPayload;
    capturedPayloads.push(payload);

    await route.fulfill({
      contentType: "application/json",
      status: 200,
      body: JSON.stringify({
        project_title: payload.project_title ?? null,
        status: "preview_ready",
        preview: {
          source: {
            filename: payload.filename,
            content_type: null,
            file_size_bytes: null,
            source_type: payload.source_type ?? "docx",
            checksum: null,
          },
          extracted_text: payload.extracted_text,
          preview_text: payload.extracted_text,
          character_count: payload.extracted_text.length,
          paragraph_count: 1,
          detected_title: "旧影院来信",
          warnings: [],
          metadata: {
            safe_preview_truncated: false,
            source_type: payload.source_type ?? "docx",
          },
        },
        context_options: payload.context_options ?? null,
        next_required_action: "user_confirm_import_action",
      }),
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

async function editFirstCharacterFields(page: Page) {
  await page.getByTestId("start-script-editing").click();
  await page.getByTestId("character-name-editor-0").fill(editedCharacterName);
  await page.getByTestId("character-personality-editor-0").fill(editedCharacterPersonality);
  await page.getByTestId("character-arc-editor-0").fill(editedCharacterArc);
  await page.getByTestId("save-script-editing").click();
}

async function editFirstEpisodeFields(page: Page) {
  await page.getByTestId("start-script-editing").click();
  await page.getByTestId("episode-title-editor-0").fill(editedEpisodeTitle);
  await page.getByTestId("episode-summary-editor-0").fill(editedEpisodeSummary);
  await page.getByTestId("episode-hook-editor-0").fill(editedEpisodeHook);
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

  test("shows document import preview controls for the film adaptation entry", async ({ page }) => {
    const importPayloads: DocumentImportPayload[] = [];
    await mockDocumentImportPreview(page, importPayloads);
    await page.goto("/");
    await login(page);

    await page.getByTestId("creation-entry-card-adaptation").click();
    await page.getByTestId("creation-entry-card-film").click();

    await expect(page.getByText("电影剧本改编短剧本")).toBeVisible();
    await expect(page.getByTestId("document-import-panel")).toBeVisible();
    await expect(page.getByText("导入剧本文档内容")).toBeVisible();
    await expect(page.getByRole("button", { name: "生成导入预览" })).toBeVisible();
    await expect(page.getByText(/mock|本地后端|后端 mock/i)).toHaveCount(0);

    await page.getByLabel("文件名").fill("old-cinema-letter.docx");
    await page.getByLabel("文档文本").fill("旧影院来信\n放映员收到一封写给未来的信。");
    await page.getByRole("button", { name: "生成导入预览" }).click();

    await expect(page.getByText("文档导入预览")).toBeVisible();
    expect(importPayloads[0].context_options?.context_policy).toBe("current_project_only");
    expect(importPayloads[0].context_options?.source_stage).toBe("imported_document");
    expect(importPayloads[0].context_options?.project_id).toBe("project_creation_default");
    expect(importPayloads[0].context_options?.session_id).toBe("session_creation_default");
    expect(importPayloads[0].context_options?.request_id).toMatch(/^request_\d+$/);
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
    const exportPayloads: DocumentExportPayload[] = [];
    await context.grantPermissions(["clipboard-read", "clipboard-write"]);
    await mockScriptGeneration(page);
    await mockDocumentExport(page, exportPayloads);
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

    const jsonDownloadPromise = page.waitForEvent("download");
    await page.getByTestId("download-script-json").click();
    await jsonDownloadPromise;
    const jsonExportPayload = exportPayloads.find((payload) => payload.export_format === "json");

    expect(jsonExportPayload?.structured_payload?.project_title).toBe(editedScriptTitle);
    expect(jsonExportPayload?.context_options?.source_stage).toBe("export");
    expect(jsonExportPayload?.context_options?.context_policy).toBe("current_project_only");
    expect(jsonExportPayload?.context_options?.project_id).toBe("project_creation_default");
    expect(jsonExportPayload?.context_options?.session_id).toBe("session_creation_default");
    expect(jsonExportPayload?.context_options?.request_id).toMatch(/^request_\d+$/);

    const downloadPromise = page.waitForEvent("download");
    await page.getByTestId("download-script-txt").click();
    const download = await downloadPromise;
    const downloadPath = await download.path();

    expect(downloadPath).not.toBeNull();
    const downloadedText = await readFile(downloadPath as string, "utf-8");
    const txtExportPayload = exportPayloads.find((payload) => payload.export_format === "txt");

    expect(txtExportPayload?.project_title).toBe(editedScriptTitle);
    expect(txtExportPayload?.structured_payload?.project_title).toBe(editedScriptTitle);
    expect(txtExportPayload?.structured_payload?.logline).toBe(editedScriptLogline);
    expect(txtExportPayload?.structured_payload?.world_setting).toBe(editedWorldSetting);
    expect(txtExportPayload?.metadata?.edited).toBe(true);
    expect(txtExportPayload?.metadata?.exported_from).toBe("creation_home");
    expect(txtExportPayload?.context_options?.source_stage).toBe("export");
    expect(txtExportPayload?.context_options?.context_policy).toBe("current_project_only");
    expect(txtExportPayload?.context_options?.project_id).toBe("project_creation_default");
    expect(txtExportPayload?.context_options?.session_id).toBe("session_creation_default");
    expect(txtExportPayload?.context_options?.request_id).toMatch(/^request_\d+$/);
    expect(downloadedText).toContain(editedScriptTitle);
    expect(downloadedText).toContain(editedScriptLogline);
    expect(downloadedText).toContain(editedWorldSetting);
  });

  test("uses edited character content for copy and text download", async ({ page, context }) => {
    const exportPayloads: DocumentExportPayload[] = [];
    await context.grantPermissions(["clipboard-read", "clipboard-write"]);
    await mockScriptGeneration(page);
    await mockDocumentExport(page, exportPayloads);
    await generateIdeaScript(page);
    await editFirstCharacterFields(page);

    await expect(page.getByText(editedCharacterName)).toBeVisible();
    await expect(page.getByText(editedCharacterPersonality)).toBeVisible();
    await expect(page.getByText(editedCharacterArc)).toBeVisible();

    await page.getByTestId("copy-script-json").click();
    const clipboardText = await page.evaluate(() => navigator.clipboard.readText());
    const copiedScript = JSON.parse(clipboardText) as {
      characters: Array<{
        name: string;
        personality: string;
        arc: string;
      }>;
    };

    expect(copiedScript.characters[0].name).toBe(editedCharacterName);
    expect(copiedScript.characters[0].personality).toBe(editedCharacterPersonality);
    expect(copiedScript.characters[0].arc).toBe(editedCharacterArc);
    expect(copiedScript.characters[0].name).not.toBe(generatedScriptFixture.characters[0].name);
    expect(copiedScript.characters[0].personality).not.toBe(
      generatedScriptFixture.characters[0].personality,
    );
    expect(copiedScript.characters[0].arc).not.toBe(generatedScriptFixture.characters[0].arc);

    const downloadPromise = page.waitForEvent("download");
    await page.getByTestId("download-script-txt").click();
    const download = await downloadPromise;
    const downloadPath = await download.path();

    expect(downloadPath).not.toBeNull();
    const downloadedText = await readFile(downloadPath as string, "utf-8");
    const txtExportPayload = exportPayloads.find((payload) => payload.export_format === "txt");

    expect(txtExportPayload?.structured_payload?.characters?.[0]?.name).toBe(editedCharacterName);
    expect(txtExportPayload?.structured_payload?.characters?.[0]?.personality).toBe(
      editedCharacterPersonality,
    );
    expect(txtExportPayload?.structured_payload?.characters?.[0]?.arc).toBe(editedCharacterArc);
    expect(downloadedText).toContain(editedCharacterName);
    expect(downloadedText).toContain(editedCharacterPersonality);
    expect(downloadedText).toContain(editedCharacterArc);
  });

  test("uses edited episode content for copy and text download", async ({ page, context }) => {
    const exportPayloads: DocumentExportPayload[] = [];
    await context.grantPermissions(["clipboard-read", "clipboard-write"]);
    await mockScriptGeneration(page);
    await mockDocumentExport(page, exportPayloads);
    await generateIdeaScript(page);
    await editFirstEpisodeFields(page);

    await expect(page.getByText(editedEpisodeTitle)).toBeVisible();
    await expect(page.getByText(editedEpisodeSummary)).toBeVisible();
    await expect(page.getByText(`钩子：${editedEpisodeHook}`)).toBeVisible();

    await page.getByTestId("copy-script-json").click();
    const clipboardText = await page.evaluate(() => navigator.clipboard.readText());
    const copiedScript = JSON.parse(clipboardText) as {
      episodes: Array<{
        title: string;
        summary: string;
        hook: string;
      }>;
    };

    expect(copiedScript.episodes[0].title).toBe(editedEpisodeTitle);
    expect(copiedScript.episodes[0].summary).toBe(editedEpisodeSummary);
    expect(copiedScript.episodes[0].hook).toBe(editedEpisodeHook);
    expect(copiedScript.episodes[0].title).not.toBe(generatedScriptFixture.episodes[0].title);
    expect(copiedScript.episodes[0].summary).not.toBe(generatedScriptFixture.episodes[0].summary);
    expect(copiedScript.episodes[0].hook).not.toBe(generatedScriptFixture.episodes[0].hook);

    const downloadPromise = page.waitForEvent("download");
    await page.getByTestId("download-script-txt").click();
    const download = await downloadPromise;
    const downloadPath = await download.path();

    expect(downloadPath).not.toBeNull();
    const downloadedText = await readFile(downloadPath as string, "utf-8");
    const txtExportPayload = exportPayloads.find((payload) => payload.export_format === "txt");

    expect(txtExportPayload?.structured_payload?.episodes?.[0]?.title).toBe(editedEpisodeTitle);
    expect(txtExportPayload?.structured_payload?.episodes?.[0]?.summary).toBe(editedEpisodeSummary);
    expect(txtExportPayload?.structured_payload?.episodes?.[0]?.hook).toBe(editedEpisodeHook);
    expect(downloadedText).toContain(editedEpisodeTitle);
    expect(downloadedText).toContain(editedEpisodeSummary);
    expect(downloadedText).toContain(editedEpisodeHook);
  });

  test("downloads edited script as docx through document export file endpoint", async ({ page }) => {
    const exportFilePayloads: DocumentExportPayload[] = [];
    await mockScriptGeneration(page);
    await mockDocumentExportFile(page, exportFilePayloads);
    await generateIdeaScript(page);
    await editGeneratedScriptBasicFields(page);

    const downloadPromise = page.waitForEvent("download");
    await page.getByTestId("download-script-docx").click();
    const download = await downloadPromise;

    const docxPayload = exportFilePayloads[0];
    expect(docxPayload.export_format).toBe("docx");
    expect(docxPayload.structured_payload?.project_title).toBe(editedScriptTitle);
    expect(docxPayload.structured_payload?.logline).toBe(editedScriptLogline);
    expect(docxPayload.structured_payload?.world_setting).toBe(editedWorldSetting);
    expect(docxPayload.metadata?.edited).toBe(true);
    expect(docxPayload.metadata?.exported_from).toBe("creation_home");
    expect(docxPayload.context_options?.source_stage).toBe("export");
    expect(docxPayload.context_options?.context_policy).toBe("current_project_only");
    expect(docxPayload.context_options?.project_id).toBe("project_creation_default");
    expect(docxPayload.context_options?.session_id).toBe("session_creation_default");
    expect(docxPayload.context_options?.request_id).toMatch(/^request_\d+$/);
    expect(download.suggestedFilename()).toBe("dramora-short-drama-script.docx");
  });
});
