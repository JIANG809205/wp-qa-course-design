@Test
public void contributorShouldSeeOnlySubmitForReviewButton() {
    // Given: Login as contributor
    loginPage.loginAsContributor("contributorUser", "password123");
    
    // When: Navigate to create new article page
    dashboardPage.navigateToNewArticle();
    
    // Then: Verify only 'Submit for Review' button is visible, not 'Publish' button
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    WebElement submitForReviewButton = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("submit-for-review-button")));
    Assert.assertTrue(submitForReviewButton.isDisplayed(), "Submit for Review button should be visible");

    try {
        WebElement publishButton = driver.findElement(By.id("publish-button"));
        Assert.fail("Publish button should not be present for contributor");
    } catch (NoSuchElementException e) {
        // Expected: Publish button does not exist
    }
}