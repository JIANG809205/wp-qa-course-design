@Test
public void searchArticleInAdminPanel() {
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    driver.get("https://admin.example.com/articles");
    WebElement searchInput = wait.until(ExpectedConditions.visibilityOfElementLocated(By.name("search")));
    searchInput.clear();
    searchInput.sendKeys("test keyword");
    searchInput.sendKeys(Keys.ENTER);
    List<WebElement> resultItems = wait.until(ExpectedConditions.presenceOfAllElementsLocatedBy(By.cssSelector(".article-item")));
    Assert.assertFalse(resultItems.isEmpty(), "No articles found in search results");
    for (WebElement item : resultItems) {
        Assert.assertTrue(item.getText().toLowerCase().contains("test keyword"), "Article does not match search keyword");
    }
}