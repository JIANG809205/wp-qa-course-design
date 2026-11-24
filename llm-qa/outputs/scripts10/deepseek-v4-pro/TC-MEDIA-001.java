@Test
public void testUploadImageSuccessfully() {
    WebDriver driver = new ChromeDriver();
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));

    try {
        driver.get("https://example.com/media");

        WebElement fileInput = wait.until(ExpectedConditions.presenceOfElementLocated(By.cssSelector("input[type='file']")));
        fileInput.sendKeys(System.getProperty("user.dir") + "/src/test/resources/test-image.jpg");

        WebElement uploadButton = driver.findElement(By.id("upload-btn"));
        uploadButton.click();

        WebElement thumbnail = wait.until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector(".thumbnail img")));
        Assert.assertTrue(thumbnail.isDisplayed(), "Thumbnail should be displayed after successful upload");
    } finally {
        driver.quit();
    }
}