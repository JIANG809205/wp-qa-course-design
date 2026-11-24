@Test
public void submitCommentForReview() {
    driver.get("https://example.com/article");
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    WebElement articleContent = wait.until(ExpectedConditions.presenceOfElementLocated(By.id("article-content")));
    WebElement commentInput = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("comment-input")));
    commentInput.sendKeys("This is a test comment.");
    WebElement submitButton = wait.until(ExpectedConditions.elementToBeClickable(By.id("submit-comment")));
    submitButton.click();
    WebElement toastMessage = wait.until(ExpectedConditions.visibilityOfElementLocated(By.className("toast-message")));
    Assert.assertEquals(toastMessage.getText(), "提示等待审核");
}