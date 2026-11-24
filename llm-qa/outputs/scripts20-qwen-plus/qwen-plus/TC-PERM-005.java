@Test
public void authorCannotDeleteOthersArticle() {
    // Given: 以作者身份登录
    loginAsAuthor();
    
    // When: 尝试删除他人文章
    navigateToOthersArticle();
    
    // Then: 验证无删除入口或操作被拒
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    try {
        WebElement deleteButton = wait.until(ExpectedConditions.elementToBeClickable(By.id("delete-button")));
        Assert.fail("Delete button should not be present or clickable for others' article");
    } catch (TimeoutException e) {
        // Expected: delete button not found or not clickable
    }
    
    // Additional check: verify permission denied message if shown
    try {
        WebElement deniedMessage = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("permission-denied-message")));
        Assert.assertTrue(deniedMessage.isDisplayed());
    } catch (TimeoutException e) {
        // Also acceptable if no UI element appears — just absence of delete capability
    }
}