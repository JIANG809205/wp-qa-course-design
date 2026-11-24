@Test
public void testContributorHasNoPublishButton() {
    WebDriver driver = new ChromeDriver();
    driver.manage().window().maximize();
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));

    driver.get("https://example.com/login");
    WebElement usernameField = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("username")));
    usernameField.sendKeys("contributor");
    driver.findElement(By.id("password")).sendKeys("contributor_pass");
    driver.findElement(By.id("loginButton")).click();

    driver.get("https://example.com/wp-admin/post-new.php");
    WebElement submitButton = wait.until(ExpectedConditions.visibilityOfElementLocated(By.xpath("//button[contains(text(),'提交复审') or contains(text(),'Submit for Review')]")));
    assertTrue(submitButton.isDisplayed(), "提交复审按钮应当可见");

    List<WebElement> publishButtons = driver.findElements(By.xpath("//button[contains(text(),'发布') or contains(text(),'Publish')]"));
    assertEquals(publishButtons.size(), 0, "不应当存在发布按钮");

    driver.quit();
}