@Test
public void testRestPaginationBoundary() {
    WebDriver driver = new ChromeDriver();
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    driver.get("https://api.example.com/items?per_page=101");
    String statusCode = driver.findElement(By.tagName("body")).getText();
    Assert.assertTrue(statusCode.contains("400") || statusCode.contains("Bad Request") || statusCode.contains("参数错误"));
    driver.quit();
}