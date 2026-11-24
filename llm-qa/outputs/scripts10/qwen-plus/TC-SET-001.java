@Test
public void updateSiteTitle() {
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    driver.get("http://example.com/wp-admin/options-general.php");
    wait.until(ExpectedConditions.presenceOfElementLocated(By.id("blogname")));
    WebElement titleField = driver.findElement(By.id("blogname"));
    titleField.clear();
    titleField.sendKeys("New Site Title");
    driver.findElement(By.id("submit")).click();
    wait.until(ExpectedConditions.alertIsPresent());
    driver.switchTo().alert().accept();
    driver.get("http://example.com");
    WebElement headerTitle = wait.until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector("h1.site-title")));
    Assert.assertEquals(headerTitle.getText(), "New Site Title");
}