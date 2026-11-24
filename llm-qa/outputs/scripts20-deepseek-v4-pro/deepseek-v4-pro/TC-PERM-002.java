@Test
public void subscriberCannotAccessAdminEditPosts() {
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));

    // 登录
    driver.get("https://your-site.com/wp-login.php");
    wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("user_login"))).sendKeys("subscriber");
    driver.findElement(By.id("user_pass")).sendKeys("password");
    driver.findElement(By.id("wp-submit")).click();

    // 等待管理栏出现，确认登录成功
    wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("wpadminbar")));

    // 尝试访问管理后台的帖子列表
    String forbiddenUrl = "https://your-site.com/wp-admin/edit.php";
    driver.get(forbiddenUrl);

    // 显式等待，直到当前URL不再等于被禁止的页面（订阅者会被重定向或停留在其他页面）
    wait.until(ExpectedConditions.not(ExpectedConditions.urlToBe(forbiddenUrl)));

    // 断言：订阅者无法访问目标页面
    Assert.assertFalse(driver.getCurrentUrl().contains("/wp-admin/edit.php"),
        "Subscriber must be denied access to admin edit posts page.");
}