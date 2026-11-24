@Test
public void testSaveArticleDraft() {
    // 假设 driver 已经通过 TestNG 的 @BeforeMethod 初始化
    WebDriver driver = ...;

    // 进入新建文章页面
    driver.get("https://example.com/article/new");

    // 显式等待：标题输入框可见
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    WebElement titleInput = wait.until(
        ExpectedConditions.visibilityOfElementLocated(By.id("article-title"))
    );

    // 填写标题
    titleInput.sendKeys("自动化测试草稿");

    // 点击保存草稿按钮
    WebElement saveDraftButton = wait.until(
        ExpectedConditions.elementToBeClickable(By.id("save-draft-btn"))
    );
    saveDraftButton.click();

    // 验证提示信息
    WebElement successMessage = wait.until(
        ExpectedConditions.visibilityOfElementLocated(By.cssSelector(".draft-success-message"))
    );
    Assert.assertTrue(
        successMessage.getText().contains("草稿已更新"),
        "未包含预期的提示文字"
    );
}