@Test
public void adminSuccessfulLogin() {
    WebDriver driver = new ChromeDriver();
    driver.get("https://example.com/wp-login.php");
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));

    WebElement usernameField = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("user_login")));
    WebElement passwordField = driver.findElement(By.id("user_pass"));
    WebElement loginButton = driver.findElement(By.id("wp-submit"));

    usernameField.sendKeys("admin");
    passwordField.sendKeys("Admin@2026");
    loginButton.click();

    wait.until(ExpectedConditions.urlContains("/wp-admin/"));
    WebElement dashboardHeader = wait.until(ExpectedConditions.presenceOfElementLocated(By.cssSelector("#wpadminbar")));
    Assert.assertNotNull(dashboardHeader, "Login failed – wp-admin bar not found");

    driver.quit();
}