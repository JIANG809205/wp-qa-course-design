@Test
public void loginWithIncorrectPasswordShouldFail() {
    driver.get("https://example.com/login");
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));

    WebElement usernameField = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("username")));
    WebElement passwordField = driver.findElement(By.id("password"));
    WebElement submitButton = driver.findElement(By.id("login-button"));

    usernameField.sendKeys("valid_user");
    passwordField.sendKeys("wrong_password");
    submitButton.click();

    WebElement errorMessage = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("error-message")));
    Assert.assertEquals(errorMessage.getText(), "密码不正确");
}