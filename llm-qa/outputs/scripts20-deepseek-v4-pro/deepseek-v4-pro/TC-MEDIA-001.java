@Test
public void testUploadImageAndGenerateThumbnail() {
    WebDriver driver = new ChromeDriver();
    driver.manage().window().maximize();
    try {
        // 进入媒体库
        driver.get("https://example.com/media-library");

        // 选择图片
        WebElement fileInput = new WebDriverWait(driver, Duration.ofSeconds(10))
                .until(ExpectedConditions.presenceOfElementLocated(By.id("fileInput")));
        String filePath = System.getProperty("user.dir") + "/src/test/resources/test-image.jpg";
        fileInput.sendKeys(filePath);

        // 上传
        WebElement uploadButton = driver.findElement(By.id("uploadBtn"));
        uploadButton.click();

        // 显式等待缩略图出现
        WebElement thumbnail = new WebDriverWait(driver, Duration.ofSeconds(15))
                .until(ExpectedConditions.visibilityOfElementLocated(
                        By.xpath("//img[contains(@class, 'thumbnail') or contains(@src, 'thumb')]")));

        // 断言上传成功并生成缩略图
        Assert.assertTrue(thumbnail.isDisplayed(), "缩略图未显示，上传可能失败");
    } finally {
        driver.quit();
    }
}