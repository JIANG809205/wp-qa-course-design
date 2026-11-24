package com.example.tests;

import java.time.Duration;
import java.util.UUID;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.Assert;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

public class SiteSettingsTest {

    private static final String BASE_URL = "http://localhost:8080";

    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeMethod(alwaysRun = true)
    public void setUp() {
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        wait = new WebDriverWait(driver, Duration.ofSeconds(20));
    }

    @AfterMethod(alwaysRun = true)
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    @Test
    public void updateSiteTitleAndVerifyFrontendSync() {
        String newTitle = "Automation Title " + UUID.randomUUID().toString().substring(0, 8);

        driver.get(BASE_URL + "/wp-admin/options-general.php");

        WebElement titleInput = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("blogname")));
        wait.until(ExpectedConditions.elementToBeClickable(titleInput));
        titleInput.clear();
        titleInput.sendKeys(newTitle);

        WebElement saveButton = wait.until(ExpectedConditions.elementToBeClickable(By.id("submit")));
        saveButton.click();

        WebElement savedNotice = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("setting-error-settings_updated")));
        Assert.assertTrue(savedNotice.getText().contains("Settings saved"), "Settings saved confirmation was not displayed");

        driver.get(BASE_URL + "/");

        WebElement frontendTitle = wait.until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector(".site-title, h1.site-title, header h1")));
        Assert.assertEquals(frontendTitle.getText().trim(), newTitle, "Frontend site title was not synced with the new value");
    }
}