@Test
public void saveArticleDraft() {
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    driver.get("https://example.com/new-article");
    WebElement titleField = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("title")));
    titleField.sendKeys("Test Article Title");
    WebElement saveDraftButton = wait.until(ExpectedConditions.elementToBeClickable(By.id("save-draft")));
    saveDraftButton.click();
    WebElement toastMessage = wait.until(ExpectedConditions.visibilityOfElementLocated(By.className("toast-message")));
    Assert.assertEquals(toastMessage.getText(), "草稿已更新");
}