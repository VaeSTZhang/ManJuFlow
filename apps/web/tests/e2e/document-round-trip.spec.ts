import { readFile, writeFile } from "node:fs/promises";
import { expect, test, type Page } from "@playwright/test";

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
const authUserId = "user_safe_creator_001";
const authWorkspaceId = "workspace_dramora_internal";
const authSessionId = "session_safe_creator_001";
const authProjectId = "project_user_safe_creator_001_creation";

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

type DocumentImportPayload = {
  filename: string;
  extracted_text: string;
  source_type?: string;
  project_title?: string | null;
  context_options?: RequestContextOptions;
};

type DocumentImportMultipartPayload = {
  contentType: string;
  bodyText: string;
};

async function mockAuth(page: Page) {
  await page.route("**/api/auth/login", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      status: 200,
      body: JSON.stringify({
        user: {
          user_id: authUserId,
          username: "safe_creator",
          display_name: "安全测试创作者",
          role: "creator",
          status: "active",
          workspace_id: authWorkspaceId,
          created_at: null,
          updated_at: null,
          metadata: {},
        },
        session: {
          session_id: authSessionId,
          user_id: authUserId,
          workspace_id: authWorkspaceId,
          role: "creator",
          status: "active",
          expires_at: null,
          context_policy: "current_project_only",
        },
        access_token: "safe_test_token",
        token_type: "bearer",
      }),
    });
  });
}

async function login(page: Page) {
  await mockAuth(page);
  await page.getByRole("button", { name: "登录" }).click();
  await expect(page.getByRole("button", { name: "退出登录" })).toBeVisible();
  await expect(page.getByText("安全测试创作者")).toBeVisible();
  await expectNoAuthSensitiveText(page);
}

async function expectNoAuthSensitiveText(page: Page) {
  await expect(page.getByText("SafePass123", { exact: false })).toHaveCount(0);
  await expect(page.getByText("password_hash", { exact: false })).toHaveCount(0);
  await expect(page.getByText("safe_test_token", { exact: false })).toHaveCount(0);
  await expect(page.getByText("access_token", { exact: false })).toHaveCount(0);
  await expect(page.getByText("后端 mock", { exact: false })).toHaveCount(0);
  await expect(page.getByText("本地演示", { exact: false })).toHaveCount(0);
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

async function mockDocxDocumentImportPreview(
  page: Page,
  capturedPayloads: DocumentImportMultipartPayload[] = [],
) {
  await page.route("**/api/documents/import-docx-preview", async (route) => {
    const request = route.request();
    capturedPayloads.push({
      contentType: request.headers()["content-type"] ?? "",
      bodyText: request.postDataBuffer()?.toString("utf-8") ?? "",
    });

    await route.fulfill({
      contentType: "application/json",
      status: 200,
      body: JSON.stringify({
        project_title: "旧影院来信",
        status: "preview_ready",
        preview: {
          source: {
            filename: "safe-script-import.docx",
            content_type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            file_size_bytes: 128,
            source_type: "docx",
            checksum: null,
          },
          extracted_text: "旧影院来信\n放映员收到一封写给未来的信。",
          preview_text: "旧影院来信\n放映员收到一封写给未来的信。",
          character_count: 23,
          paragraph_count: 2,
          detected_title: "旧影院来信",
          warnings: [],
          metadata: {
            safe_preview_truncated: false,
            source_type: "docx",
          },
        },
        context_options: {
          user_id: authUserId,
          workspace_id: authWorkspaceId,
          project_id: authProjectId,
          session_id: authSessionId,
          request_id: "request_docx_import_e2e",
          source_stage: "imported_document",
          context_policy: "current_project_only",
        },
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

test.describe("Dramora document round-trip smoke", () => {
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
    expect(importPayloads[0].context_options?.user_id).toBe(authUserId);
    expect(importPayloads[0].context_options?.project_id).toBe(authProjectId);
    expect(importPayloads[0].context_options?.session_id).toBe(authSessionId);
    expect(importPayloads[0].context_options?.request_id).toMatch(/^request_\d+$/);
  });

  test("uploads docx file for document import preview with context options", async ({ page }, testInfo) => {
    const importPayloads: DocumentImportMultipartPayload[] = [];
    const docxPath = testInfo.outputPath("safe-script-import.docx");
    await writeFile(docxPath, Buffer.from("safe fake docx bytes for frontend route interception"));
    await mockDocxDocumentImportPreview(page, importPayloads);

    await page.goto("/");
    await login(page);
    await page.getByTestId("creation-entry-card-adaptation").click();
    await page.getByTestId("creation-entry-card-film").click();

    await expect(page.getByTestId("document-import-panel")).toBeVisible();
    await expect(page.getByTestId("docx-import-file-input")).toBeVisible();
    await expect(page.getByTestId("generate-docx-import-preview")).toBeVisible();

    await page.getByTestId("docx-import-file-input").setInputFiles(docxPath);
    await page.getByTestId("generate-docx-import-preview").click();

    await expect(page.getByText("文档导入预览")).toBeVisible();
    await expect(page.getByRole("button", { name: "填入待改编文本" })).toBeVisible();
    await expect(page.getByRole("button", { name: "追加到当前文本后" })).toBeVisible();
    await expect(page.getByRole("button", { name: "取消导入" })).toBeVisible();

    const payload = importPayloads[0];
    expect(payload.contentType).toContain("multipart/form-data");
    expect(payload.bodyText).toContain('name="file"');
    expect(payload.bodyText).toContain("safe-script-import.docx");
    expect(payload.bodyText).toContain('name="user_id"');
    expect(payload.bodyText).toContain(authUserId);
    expect(payload.bodyText).toContain('name="workspace_id"');
    expect(payload.bodyText).toContain(authWorkspaceId);
    expect(payload.bodyText).toContain('name="project_id"');
    expect(payload.bodyText).toContain(authProjectId);
    expect(payload.bodyText).toContain('name="session_id"');
    expect(payload.bodyText).toContain(authSessionId);
    expect(payload.bodyText).toContain('name="source_stage"');
    expect(payload.bodyText).toContain("imported_document");
    expect(payload.bodyText).toContain('name="context_policy"');
    expect(payload.bodyText).toContain("current_project_only");
    expect(payload.bodyText).toMatch(/request_\d+/);
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
    expect(jsonExportPayload?.context_options?.user_id).toBe(authUserId);
    expect(jsonExportPayload?.context_options?.project_id).toBe(authProjectId);
    expect(jsonExportPayload?.context_options?.session_id).toBe(authSessionId);
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
    expect(txtExportPayload?.context_options?.user_id).toBe(authUserId);
    expect(txtExportPayload?.context_options?.project_id).toBe(authProjectId);
    expect(txtExportPayload?.context_options?.session_id).toBe(authSessionId);
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
    expect(docxPayload.context_options?.user_id).toBe(authUserId);
    expect(docxPayload.context_options?.project_id).toBe(authProjectId);
    expect(docxPayload.context_options?.session_id).toBe(authSessionId);
    expect(docxPayload.context_options?.request_id).toMatch(/^request_\d+$/);
    expect(download.suggestedFilename()).toBe("dramora-short-drama-script.docx");
  });
});
