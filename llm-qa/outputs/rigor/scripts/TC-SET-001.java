package com.example.tests;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

import java.time.Duration;

import static org.testng.Assert.assertEquals;
import static org.testng.Assert.assertTrue;

public class SiteSettingsTest {

    private static final String BASE_URL = System.getProperty("baseUrl", "http://localhost:8080");
    private static final String ADMIN_USER = System.getProperty("adminUser", "admin");
    private static final String ADMIN_PASSWORD = System.getProperty("adminPassword", "admin123");
    private static final String NEW_TITLE = "自动化测试站点标题";

    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeMethod
    public void setUp() {
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        wait = new WebDriverWait(driver, Duration.ofSeconds(20));
    }

    @Test
    public void updateSiteTitle() {
        driver.get(BASE_URL + "/admin/login");

        WebElement usernameInput = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("username")));
        usernameInput.clear();
        usernameInput.sendKeys(ADMIN_USER);

        WebElement passwordInput = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("password")));
        passwordInput.clear();
        passwordInput.sendKeys(ADMIN_PASSWORD);

        wait.until(ExpectedConditions.elementToBeClickable(By.cssSelector("button[type='submit'], input[type='submit']"))).click();

        wait.until(ExpectedConditions.elementToBeClickable(By.linkText("设置"))).click();
        wait.until(ExpectedConditions.elementToBeClickable(By.linkText("常规"))).click();

        WebElement titleInput = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("blogname")));
        titleInput.clear();
        titleInput.sendKeys(NEW_TITLE);
        assertEquals(titleInput.getAttribute("value"), NEW_TITLE, "标题输入框内容未更新");

        wait.until(ExpectedConditions.elementToBeClickable(By.id("submit"))).click();

        WebElement savedNotice = wait.until(ExpectedConditions.visibilityOfElementLocated(
                By.cssSelector("#setting-error-settings_updated, .notice-success, .updated")));
        assertTrue(savedNotice.isDisplayed(), "保存成功提示未出现");

        driver.get(BASE_URL);

        WebElement frontTitle = wait.until(ExpectedConditions.visibilityOfElementLocated(
                By.cssSelector("h1.site-title, header .site-title, title")));
        String actualTitle = frontTitle.getText().trim().isEmpty()
                ? driver.getTitle().trim()
                : frontTitle.getText().trim();
        assertTrue(actualTitle.contains(NEW_TITLE), "前台标题未同步更新，实际为：" + actualTitle);
    }

    @AfterMethod(alwaysRun = true)
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
}