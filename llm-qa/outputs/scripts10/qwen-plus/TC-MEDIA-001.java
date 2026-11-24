@Test
public void uploadImageSuccessfully() {
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    driver.get("https://example.com/media-library");
    wait.until(ExpectedConditions.titleContains("媒体库"));
    
    WebElement mediaLibraryLink = wait.until(ExpectedConditions.elementToBeClickable(By.linkText("媒体库")));
    mediaLibraryLink.click();
    
    WebElement fileInput = wait.until(ExpectedConditions.presenceOfElementLocated(By.cssSelector("input[type='file']")));
    fileInput.sendKeys("/path/to/test-image.jpg");
    
    WebElement uploadButton = wait.until(ExpectedConditions.elementToBeClickable(By.id("upload-btn")));
    uploadButton.click();
    
    WebElement thumbnail = wait.until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector(".thumbnail img")));
    Assert.assertTrue(thumbnail.isDisplayed(), "Thumbnail should be displayed after successful upload");
}