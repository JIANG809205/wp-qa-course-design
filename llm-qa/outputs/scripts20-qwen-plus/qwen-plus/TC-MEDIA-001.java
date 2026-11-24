@Test
public void uploadImageSuccessfully() {
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    driver.get("https://example.com/media-library");
    wait.until(ExpectedConditions.titleContains("媒体库"));
    
    WebElement uploadButton = wait.until(ExpectedConditions.elementToBeClickable(By.id("upload-btn")));
    uploadButton.click();
    
    WebElement fileInput = driver.findElement(By.id("file-input"));
    fileInput.sendKeys("/path/to/test-image.jpg");
    
    WebElement submitButton = wait.until(ExpectedConditions.elementToBeClickable(By.id("submit-upload")));
    submitButton.click();
    
    WebElement thumbnail = wait.until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector(".thumbnail img")));
    Assert.assertTrue(thumbnail.isDisplayed(), "Thumbnail should be displayed after successful upload");
}