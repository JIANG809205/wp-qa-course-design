@Test
public void testPermalinkStructureUpdate() {
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    driver.get("http://localhost/wp-admin/options-permalink.php");
    wait.until(ExpectedConditions.presenceOfElementLocated(By.id("permalink_structure")));
    WebElement postNameRadio = driver.findElement(By.id("sample-permalink"));
    postNameRadio.click();
    WebElement saveButton = driver.findElement(By.name("submit"));
    saveButton.click();
    wait.until(ExpectedConditions.alertIsPresent());
    String alertText = driver.switchTo().alert().getText();
    driver.switchTo().alert().accept();
    Assert.assertTrue(alertText.contains("已更新"));
}