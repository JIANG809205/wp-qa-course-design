@Test
public void subscriberCannotAccessAdminDashboard() {
    driver.get("https://example.com/wp-login.php");
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    
    WebElement usernameField = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("user_login")));
    WebElement passwordField = driver.findElement(By.id("user_pass"));
    WebElement loginButton = driver.findElement(By.id("wp-submit"));
    
    usernameField.sendKeys("subscriber_user");
    passwordField.sendKeys("subscriber_pass");
    loginButton.click();
    
    wait.until(ExpectedConditions.urlContains("wp-admin"));
    
    driver.get("https://example.com/wp-admin/edit.php");
    
    WebElement accessDeniedMessage = wait.until(ExpectedConditions.presenceOfElementLocated(By.xpath("//*[contains(text(), 'You do not have sufficient permissions')] | //*[contains(text(), '被拒绝')]")));
    
    Assert.assertTrue(accessDeniedMessage.isDisplayed());
}