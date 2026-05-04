import { expect, test } from "@playwright/test";

const blockedUiPhrases = [
  "后端 mock",
  "本地后端",
  "本地演示",
  "使用后端默认",
  "MVP",
  "第五阶段",
];

async function login(page: import("@playwright/test").Page) {
  await page.getByRole("button", { name: "登录" }).click();
  await expect(page.getByRole("button", { name: "退出登录" })).toBeVisible();
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
});
