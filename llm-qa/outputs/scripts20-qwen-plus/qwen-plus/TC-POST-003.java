@Test
public void testScheduleArticlePost() {
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    driver.findElement(By.id("new-article-button")).click();
    wait.until(ExpectedConditions.elementToBeClickable(By.id("schedule-time-input"))).sendKeys("2025-12-31T23:59");
    driver.findElement(By.id("save-button")).click();
    String statusText = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("status-label"))).getText();
    Assert.assertEquals(statusText.trim(), "已安排");
}