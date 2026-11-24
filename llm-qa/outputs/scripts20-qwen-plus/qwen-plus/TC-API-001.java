@Test
public void testAnonymousReadPostList() {
    WebDriver driver = new ChromeDriver();
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    driver.get("http://localhost:8000/wp-json/wp/v2/posts");

    try {
        String responseBody = driver.getPageSource();
        Assert.assertTrue(responseBody.contains("\"status\":\"publish\""), "Response must contain only published posts");
    } finally {
        driver.quit();
    }
}