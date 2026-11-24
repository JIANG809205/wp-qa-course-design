package com.example.tests;

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

import java.time.Duration;

public class PostRecycleBinTest {

    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeMethod
    public void setUp() {
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        wait = new WebDriverWait(driver, Duration.ofSeconds(15));
    }

    @Test
    public void movePostToRecycleBinAndRestore() {
        driver.get("http://localhost:8080/admin/posts");
        wait.until(ExpectedConditions.urlContains("/admin/posts"));

        By postTableRows = By.cssSelector("table.post-list tbody tr");
        wait.until(ExpectedConditions.visibilityOfElementLocated(postTableRows));

        WebElement firstRow = wait.until(ExpectedConditions.elementToBeClickable(
                By.cssSelector("table.post-list tbody tr:first-child")));
        String postTitle = firstRow.findElement(By.cssSelector("td.title")).getText().trim();
        Assert.assertFalse(postTitle.isEmpty(), "Post title should not be empty before moving to trash");

        firstRow.findElement(By.cssSelector("button.move-to-trash")).click();
        wait.until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector(".toast-success")));
        wait.until(ExpectedConditions.invisibilityOfElementLocated(
                By.xpath("//table[contains(@class,'post-list')]//td[normalize-space()='" + postTitle + "']")));

        wait.until(ExpectedConditions.elementToBeClickable(By.cssSelector("a[href*='recycle-bin']"))).click();
        wait.until(ExpectedConditions.urlContains("recycle-bin"));

        By trashedRow = By.xpath("//table[contains(@class,'post-list')]//tr[.//td[normalize-space()='" + postTitle + "']]");
        WebElement trashedRowElement = wait.until(ExpectedConditions.visibilityOfElementLocated(trashedRow));

        trashedRowElement.findElement(By.cssSelector("button.restore")).click();
        wait.until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector(".toast-success")));
        wait.until(ExpectedConditions.invisibilityOfElementLocated(trashedRow));

        wait.until(ExpectedConditions.elementToBeClickable(By.cssSelector("a[href='/admin/posts']"))).click();
        wait.until(ExpectedConditions.urlContains("/admin/posts"));

        WebElement restoredRow = wait.until(ExpectedConditions.visibilityOfElementLocated(trashedRow));
        Assert.assertTrue(restoredRow.isDisplayed(), "Restored post should be listed in the article list");

        String status = restoredRow.findElement(By.cssSelector("td.status")).getText().trim();
        Assert.assertEquals(status, "已发布", "Restored post status should be published");
    }

    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
}