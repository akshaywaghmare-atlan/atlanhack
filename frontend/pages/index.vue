<template>
    <div class="flex w-full h-full">
        <div class="flex w-full h-full">
            <div id="app" class="flex flex-col basis-full">
                <div class="flex items-center justify-between max-w-[896px] min-w-[896px] m-auto my-8">
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
                <div ref="formContainer"></div>
                <div ref="navigationContainer"
                    class="fixed bottom-0 w-full bg-white border-t border-solid border-slate-200"></div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import '../assets/css/main.css';
import api from '../api';
import formConfig from '../assets/formConfig';
import * as sdk from "@atlanhq/application-ui-sdk";

const formContainer = ref(null);
const navigationContainer = ref(null);

onMounted(() => {
    // If formContainer and navigationContainer are not null, render the form
    if (formContainer.value && navigationContainer.value) {
        const { FormBuilder } = sdk;
        const options = {
            api,                                              // API client
            config: formConfig,                               // Form configuration
            container: formContainer.value,                   // Container to render the form
            navigationContainer: navigationContainer.value    // Container to render the navigation
        }
        const formBuilder = new FormBuilder(options);
        formBuilder.render();
    }
});
</script>