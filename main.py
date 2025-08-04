import re
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

#configure
search_query = "python tutorial"
num_videos = 5
num_recommended = 3

#chrome setup
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

try:
    driver.get("https://www.youtube.com")

    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, ".//*[@id='guide-content']"))
        )

        # Searching
        wait = WebDriverWait(driver, 10)
        search_box = wait.until(EC.presence_of_element_located((By.NAME, "search_query")))
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.RETURN)
        try:
            # need to change your progress bar
            wait.until(EC.presence_of_element_located((By.XPATH, ".//ytd-video-renderer")))
            time.sleep(3)
        except TimeoutException:
            print("Search results took too long to load.")

        print("loading videos after search")
        #because of unnecessary video i.e ad,short vid have no url
        #results = driver.find_elements(By.XPATH, ".//ytd-video-renderer")[1:num_videos+1]

        results=[
            res for res in driver.find_elements(By.XPATH, ".//ytd-video-renderer")
            if(
                res.find_element(By.XPATH, ".//*[@id='video-title']").get_attribute("href") and
                "/shorts/" not in res.find_element(By.XPATH, ".//*[@id='video-title']").get_attribute("href")
            )
            ][:num_videos]

        print ("length of results is ",len(results))
        videos_data=[]
        rec_data=[]

        # Question what would happen if you dont get results?
        if not results:
            print(" No results found! Still Waiting!")
            time.sleep(3)
            results = [
                    res for res in driver.find_elements(By.XPATH, ".//ytd-video-renderer")
                    if res.find_element(By.XPATH, ".//*[@id='video-title']").get_attribute("href")
                    ][:num_videos]


        for result in results:
            title_el = result.find_element(By.XPATH, ".//*[@id='video-title']")
            title = title_el.get_attribute("title")
            url = title_el.get_attribute("href")
            if url is None:
                print('waiting for url to load')
                time.sleep(5)
                title_el = result.find_element(By.XPATH, ".//*[@id='video-title']")
                title = title_el.get_attribute("title")
                url = title_el.get_attribute("href")

            #view,age section
            metadata_elements = result.find_elements(By.CSS_SELECTOR, "div#metadata-line span")
            metadata = [re.sub(r'\s+', ' ', m.text.strip()) for m in metadata_elements if m.text.strip()]
            views = metadata[0] if len(metadata) > 0 else "N/A"
            age = metadata[1] if len(metadata) > 1 else "N/A"

            print(f'loading {url}')
            # Open video page
            title_el.click()

            # check if the video is loaded fully
            try:
                time.sleep(1)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-watch-next-secondary-results-renderer"))
                )

            except TimeoutException:
                print("Video page took too long to load.")

            #  Get channel
            try:
                channel_video = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, ".//*[@id='owner']//*[@id='channel-name']//a"))
                ).text.strip()
            except TimeoutException:
                try:
                    channel_video = driver.find_element(By.XPATH, ".//*[@class='style-scope ytd-channel-name']").text.strip()
                except:
                    channel_video = "N/A"

            #populating video list
            video_dict = {"Title": {title}, "Channel": {channel_video},  "Views": {views}, "Age": {age}, "URL": {url} }
            videos_data.append(video_dict)

            # Wait for recommended videos to load
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-compact-video-renderer"))
                )
            except TimeoutException:
                print("⚠️ Recommended videos took too long to load.")

            # Now extract recommended videos
            recommended = driver.find_elements(By.XPATH,".//yt-lockup-view-model")[1:num_recommended+1]

            main_dict = {}

            print('number of recommended videos', len(recommended))

            i = 1
            for rec in recommended:
                try:
                    rec_title = rec.find_element(By.XPATH, ".//a[contains(@class, 'wiz__title')]").text.strip()
                    rec_url = rec.find_element(By.XPATH, ".//a[contains(@class, 'wiz__title')]").get_attribute("href")
                    rec_channel = rec.find_element(By.XPATH,".//div[contains(@class, 'yt-content-metadata-view-model-wiz__metadata-row')][1]").text.strip()
                    rec_views = rec.find_element(By.XPATH,".//div[contains(@class, 'yt-content-metadata-view-model-wiz__metadata-row')][2]").text.strip()


                    # Populate sub dictionary with strings (not sets)
                    sub_dict = {
                        "Title": rec_title,
                         "Channel": rec_channel,
                         "Views": rec_views,
                         "URL": rec_url
                    }

                    # Add to main dictionary
                    main_dict[f"video {i}"] = sub_dict
                    i += 1

                except Exception as e:
                    print(f"⚠️ Error loading recommended video {i}: {e}")

            #populating recommendation list with main dictionaries
            rec_data.append(main_dict)

            # Go back to search results
            driver.back()
            time.sleep(5)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, ".//ytd-video-renderer"))
            )

        #writing recommendations data in file
        with open("recommended_videos.txt", "a", encoding="utf-8") as f:

            for i, item in enumerate(rec_data, start=1):
                f.write(f"\n------------Recommended videos for main video {i}:-----------------\n")
                for sub_key, sub_dict in item.items():
                    f.write(f"{sub_key}:\n")
                    f.write(json.dumps(sub_dict, indent=4))
                    f.write("\n")

        #printing videos details

        for i, item in enumerate(videos_data, start=1):
            print(f"video {i}:")
            for key, value in item.items():
                print(f"  {key}: {value}")
            print()


    except:
        print("page not found")
finally:
    driver.quit()