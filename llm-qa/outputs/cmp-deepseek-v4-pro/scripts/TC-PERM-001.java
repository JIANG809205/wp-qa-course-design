@Test
public void testContributorHasNoPublishButton() {
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    driver.get("https://example.com/login");
    WebElement usernameField = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("username")));
    usernameField.sendKeys("contributor");
    WebElement passwordField = driver.findElement(By.id("password"));
    passwordField.sendKeys("contributor_password");
    driver.findElement(By.id("login-btn")).click();
    wait.until(ExpectedConditions.urlContains("/dashboard"));
    driver.get("https://example.com/wp-admin/post-new.php");
    WebElement submitForReviewBtn = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("submit-for-review")));
    Assert.assertTrue(submitForReviewBtn.isDisplayed(), "Submit for Review button should be displayed");
    List<WebElement> publishBtns = driver.findElements(By.id("publish-button"));
    Assert.assertTrue(publishBtns.isEmpty(), "Publish button should not exist for contributor");
}