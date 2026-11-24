@Test
public void submitCommentForReview() {
    driver.get("https://example.com/article/1");
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    WebElement commentBox = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("comment")));
    commentBox.sendKeys("This is a test comment.");
    WebElement submitButton = driver.findElement(By.id("submit"));
    submitButton.click();
    WebElement alert = wait.until(ExpectedConditions.visibilityOfElementLocated(By.className("alert")));
    String actualMessage = alert.getText();
    Assert.assertEquals(actualMessage, "等待审核", "The comment should be pending review.");
}