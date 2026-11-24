@Test
public void testAnonymousReadPostsList() {
    WebDriver driver = new ChromeDriver();
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    try {
        driver.get("http://localhost:8080/wp-json/wp/v2/posts");
        wait.until(ExpectedConditions.presenceOfElementLocated(By.tagName("body")));
        String responseBody = driver.getPageSource();
        Assert.assertTrue(responseBody.contains("\"status\":\"publish\""), "Response must contain only published posts");
    } finally {
        driver.quit();
    }
}