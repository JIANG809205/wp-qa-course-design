@Test
public void contributorShouldSeeOnlySubmitForReviewButton() {
    // Arrange
    loginAsContributor();
    navigateToNewArticlePage();

    // Act
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    WebElement submitForReviewButton = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("submit-for-review")));
    boolean publishButtonNotPresent = !driver.findElements(By.id("publish")).isEmpty() == false;

    // Assert
    Assert.assertTrue(submitForReviewButton.isDisplayed(), "Submit for review button should be visible");
    Assert.assertTrue(publishButtonNotPresent, "Publish button should not be present");
}