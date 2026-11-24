@Test
public void adminRepliesToComment() {
    driver.get("https://example.com/admin/comments");
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));

    WebElement firstCommentReplyButton = wait.until(
        ExpectedConditions.elementToBeClickable(By.cssSelector(".comment-item .reply-btn"))
    );
    firstCommentReplyButton.click();

    WebElement replyTextarea = wait.until(
        ExpectedConditions.visibilityOfElementLocated(By.cssSelector(".reply-form textarea"))
    );
    replyTextarea.sendKeys("This is an admin reply.");

    WebElement submitReplyButton = wait.until(
        ExpectedConditions.elementToBeClickable(By.cssSelector(".reply-form button[type='submit']"))
    );
    submitReplyButton.click();

    WebElement nestedReply = wait.until(
        ExpectedConditions.visibilityOfElementLocated(By.cssSelector(".comment-item .nested-reply"))
    );

    Assert.assertTrue(nestedReply.isDisplayed(), "Nested reply is not displayed on frontend");
}