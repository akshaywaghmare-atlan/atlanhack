<template>
    <div class="flex w-full h-full">
        <div class="leftContainer">
            <div id="app" class="flex flex-col basis-full">
                <div class="flex items-center justify-between max-w-[896px] min-w-[896px] m-auto">
                    <div class="flex items-center">
                        <img src="https://www.postgresql.org/media/img/about/press/elephant.png" alt="PostgreSQL"
                            class="w-10 h-10" />
                        <h1 class="ml-4 text-4xl font-bold text-slate-900">
                            PostgreSQL Assets
                        </h1>
                    </div>
                    <div class="flex items-center">
                        <button
                            class="w-10 h-10 p-2 text-white bg-white rounded-md shadow hover:border-blue-500 hover:shadow-lg"
                            onclick="window.open('https://ask.atlan.com/hc/en-us/articles/6329557275793-How-to-crawl-PostgreSQL', '_blank')">
                            <img src="https://assets.atlan.com/assets/file-doc.svg" alt="Docs" class="w-6 h-6" />
                        </button>
                    </div>
                </div>
                <div id="form-container" class="basis-3/4 "></div>
                <div id="navigation" class="border-t border-solid border-slate-200"></div>
            </div>
            <!-- <div id="navigation" class="fixed bottom-0 flex justify-center w-full bg-white border-t border-solid"></div> -->
        </div>
        <!-- <div id="rightContainer" class="rightContainer"></div> -->
    </div>
</template>

<script setup>
import '../styles.css';
import sdk from "../application-ui-sdk/src/index";
const { formConfig, FormBuilder, formState } = sdk;
</script>
