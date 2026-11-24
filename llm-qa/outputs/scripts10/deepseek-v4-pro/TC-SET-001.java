@Test
public void testUpdateSiteTitle() {
    WebDriver driver = new ChromeDriver();
    driver.manage().window().maximize();
    driver.get("http://example.com/wp-admin");

    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));

    // 登录（假设已处理）
    // ...

    // 进入设置 -> 常规
    wait.until(ExpectedConditions.elementToBeClickable(By.linkText("设置"))).click();
    wait.until(ExpectedConditions.elementToBeClickable(By.linkText("常规"))).click();

    // 修改站点标题
    WebElement titleInput = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("blogname")));
    String newTitle = "新标题" + System.currentTimeMillis();
    titleInput.clear();
    titleInput.sendKeys(newTitle);

    // 保存
    wait.until(ExpectedConditions.elementToBeClickable(By.id("submit"))).click();

    // 等待保存成功消息
    wait.until(ExpectedConditions.visibilityOfElementLocated(By.xpath("//div[@class='notice notice-success']")));

    // 前台验证标题同步更新
    driver.get("http://example.com");
    WebElement frontTitle = wait.until(ExpectedConditions.visibilityOfElementLocated(By.tagName("h1")));
    Assert.assertEquals(frontTitle.getText(), newTitle);

    driver.quit();
}