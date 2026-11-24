@Test
public void adminLoginSuccessfully() {
    driver.get("https://example.com/wp-login.php");
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    WebElement usernameField = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("user_login")));
    WebElement passwordField = driver.findElement(By.id("user_pass"));
    WebElement loginButton = driver.findElement(By.id("wp-submit"));
    usernameField.clear();
    usernameField.sendKeys("admin");
    passwordField.clear();
    passwordField.sendKeys("Admin@2026");
    loginButton.click();
    wait.until(ExpectedConditions.urlContains("wp-admin"));
    Assert.assertTrue(driver.getCurrentUrl().contains("wp-admin"), "Expected to be redirected to wp-admin dashboard");
}