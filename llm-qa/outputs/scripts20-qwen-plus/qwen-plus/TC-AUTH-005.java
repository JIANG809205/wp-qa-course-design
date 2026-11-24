@Test
public void testLoginWithInvalidCredentialsFiveTimes() {
    WebDriver driver = new ChromeDriver();
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    driver.get("https://example.com/login");

    WebElement usernameField = wait.until(ExpectedConditions.presenceOfElementLocated(By.id("username")));
    WebElement passwordField = driver.findElement(By.id("password"));
    WebElement loginButton = driver.findElement(By.id("login-button"));

    for (int i = 0; i < 5; i++) {
        usernameField.clear();
        passwordField.clear();
        usernameField.sendKeys("testuser");
        passwordField.sendKeys("wrongpassword" + i);
        loginButton.click();

        try {
            wait.until(ExpectedConditions.presenceOfElementLocated(By.id("captcha")));
            break;
        } catch (TimeoutException e) {
            // Continue loop if captcha not yet present
        }
    }

    boolean isCaptchaDisplayed = false;
    boolean isLockMessageDisplayed = false;
    try {
        isCaptchaDisplayed = driver.findElement(By.id("captcha")).isDisplayed();
    } catch (NoSuchElementException ignored) {
    }
    try {
        isLockMessageDisplayed = driver.findElement(By.id("lock-message")).isDisplayed();
    } catch (NoSuchElementException ignored) {
    }

    Assert.assertTrue(isCaptchaDisplayed || isLockMessageDisplayed, "Expected captcha or lock message to appear after 5 failed login attempts");
    driver.quit();
}