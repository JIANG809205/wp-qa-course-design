@Test
public void draftPublishesSuccessfully() {
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    driver.get("https://example.com/drafts");
    WebElement draftLink = wait.until(ExpectedConditions.elementToBeClickable(By.linkText("草稿")));
    draftLink.click();
    WebElement publishButton = wait.until(ExpectedConditions.elementToBeClickable(By.id("publishButton")));
    publishButton.click();
    WebElement statusElement = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("status")));
    Assert.assertEquals(statusElement.getText().trim(), "已发布");
}