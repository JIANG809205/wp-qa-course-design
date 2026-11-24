package com.example.tests;

import java.time.Duration;
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

public class ArticleDraftTest {

    private WebDriver driver;
    private WebDriverWait wait;

    private static final By NEW_ARTICLE_BUTTON = By.cssSelector("[data-testid='new-article']");
    private static final By TITLE_INPUT = By.cssSelector("input[name='title']");
    private static final By SAVE_DRAFT_BUTTON = By.cssSelector("button[data-testid='save-draft']");
    private static final By TOAST_MESSAGE = By.cssSelector(".toast, .notification, [role='alert']");

    @BeforeMethod
    public void setUp() {
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        wait = new WebDriverWait(driver, Duration.ofSeconds(15));
        driver.get("https://example.com/articles");
    }

    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    @Test(description = "TC-POST-001 保存文章草稿")
    public void saveArticleDraft() {
        WebElement newArticleButton = wait.until(ExpectedConditions.elementToBeClickable(NEW_ARTICLE_BUTTON));
        newArticleButton.click();

        String title = "Draft " + System.currentTimeMillis();
        WebElement titleInput = wait.until(ExpectedConditions.visibilityOfElementLocated(TITLE_INPUT));
        titleInput.clear();
        titleInput.sendKeys(title);

        WebElement saveDraftButton = wait.until(ExpectedConditions.elementToBeClickable(SAVE_DRAFT_BUTTON));
        saveDraftButton.click();

        WebElement toast = wait.until(ExpectedConditions.visibilityOfElementLocated(TOAST_MESSAGE));
        String toastText = toast.getText().trim();
        Assert.assertTrue(toastText.contains("草稿已更新"),
                "Expected toast to contain '草稿已更新' but was: " + toastText);
    }
}