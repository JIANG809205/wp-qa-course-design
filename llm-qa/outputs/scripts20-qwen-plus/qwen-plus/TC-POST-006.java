@Test
public void testArticleMoveToTrashAndRestore() {
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    driver.get("https://example.com/articles");
    wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("articleList")));
    WebElement trashButton = wait.until(ExpectedConditions.elementToBeClickable(By.cssSelector("button[aria-label='Move to trash']")));
    trashButton.click();
    wait.until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector(".notification.success")));
    driver.get("https://example.com/trash");
    wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("trashList")));
    WebElement restoreButton = wait.until(ExpectedConditions.elementToBeClickable(By.cssSelector("button[aria-label='Restore']")));
    restoreButton.click();
    wait.until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector(".notification.success")));
    driver.get("https://example.com/articles");
    WebElement statusBadge = wait.until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector("span.status-badge.published")));
    Assert.assertEquals(statusBadge.getText().trim(), "Published");
}