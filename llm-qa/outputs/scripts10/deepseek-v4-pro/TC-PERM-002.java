@Test
public void testSubscriberCannotAccessAdminPage() {
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    driver.get("https://example.com/wp-login.php");
    wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("user_login"))).sendKeys("subscriber");
    driver.findElement(By.id("user_pass")).sendKeys("password");
    driver.findElement(By.id("wp-submit")).click();

    driver.get("https://example.com/wp-admin/edit.php");
    WebElement errorMessage = wait.until(ExpectedConditions.visibilityOfElementLocated(
            By.cssSelector(".wp-die-message, #error-page")));

    Assert.assertTrue(
            errorMessage.getText().contains("Sorry, you are not allowed to access this page.") ||
            errorMessage.getText().contains("You do not have sufficient permissions to access this page.")
    );
}