@Test
public void testUploadOversizedFile() {
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    driver.get("https://example.com/media-library");
    WebElement mediaLibraryLink = wait.until(ExpectedConditions.elementToBeClickable(By.linkText("媒体库")));
    mediaLibraryLink.click();
    WebElement fileInput = wait.until(ExpectedConditions.presenceOfElementLocated(By.cssSelector("input[type='file']")));
    fileInput.sendKeys("/path/to/20MB-image.jpg");
    WebElement uploadButton = wait.until(ExpectedConditions.elementToBeClickable(By.id("upload-btn")));
    uploadButton.click();
    WebElement errorMessage = wait.until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector(".error-message")));
    Assert.assertTrue(errorMessage.getText().contains("文件超过大小限制"));
}