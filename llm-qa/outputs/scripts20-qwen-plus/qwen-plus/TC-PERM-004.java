@Test
public void testEditUserAccessToCreateUserPage() {
    driver.get("https://example.com/login");
    WebElement usernameField = wait.until(ExpectedConditions.elementToBeClickable(By.id("username")));
    usernameField.sendKeys("editor_user");
    driver.findElement(By.id("password")).sendKeys("editor_pass");
    driver.findElement(By.id("login-btn")).click();

    wait.until(ExpectedConditions.urlContains("dashboard"));

    driver.get("https://example.com/users/create");

    WebElement accessDeniedMessage = wait.until(ExpectedConditions.visibilityOfElementLocated(By.xpath("//h1[contains(text(), '拒绝访问')]")));
    Assert.assertTrue(accessDeniedMessage.isDisplayed(), "Expected access denied message is not displayed");
}