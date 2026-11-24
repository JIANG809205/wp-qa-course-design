package com.example.tests;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.Assert;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

import java.time.Duration;

public class AdminLoginTest {

    private static final String BASE_URL = System.getProperty("baseUrl", "http://localhost:8080");
    private static final Duration EXPLICIT_WAIT = Duration.ofSeconds(15);

    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeMethod(alwaysRun = true)
    public void setUp() {
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--headless=new", "--window-size=1920,1080", "--no-sandbox", "--disable-dev-shm-usage");
        driver = new ChromeDriver(options);
        driver.manage().timeouts().pageLoadTimeout(Duration.ofSeconds(30));
        wait = new WebDriverWait(driver, EXPLICIT_WAIT);
    }

    @AfterMethod(alwaysRun = true)
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    @Test(description = "TC-AUTH-001: administrator logs in with valid credentials and lands on wp-admin")
    public void adminCanLoginWithValidCredentials() {
        driver.get(BASE_URL + "/wp-login.php");

        WebElement usernameInput = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("user_login")));
        usernameInput.clear();
        usernameInput.sendKeys("admin");

        WebElement passwordInput = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("user_pass")));
        passwordInput.clear();
        passwordInput.sendKeys("Admin@2026");

        WebElement submitButton = wait.until(ExpectedConditions.elementToBeClickable(By.id("wp-submit")));
        submitButton.click();

        wait.until(ExpectedConditions.urlContains("/wp-admin"));

        WebElement adminMenu = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("adminmenu")));

        Assert.assertTrue(driver.getCurrentUrl().contains("/wp-admin"),
                "Expected to be redirected to wp-admin but current URL is: " + driver.getCurrentUrl());
        Assert.assertTrue(adminMenu.isDisplayed(),
                "Admin dashboard menu should be visible after successful login");
    }
}