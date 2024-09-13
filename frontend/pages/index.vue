<template>
    <div class="flex w-full h-full">
        <div class="leftContainer">
            <div id="app" class="flex flex-col basis-full">
                <div class="text-2xl font-bold text-slate-900">
                    Postgres Assets
                </div>
                <div id="form-container" class="basis-3/4 "></div>
                <div id="navigation" class="border-t border-solid border-slate-200"></div>
            </div>
            <!-- <div id="navigation" class="fixed bottom-0 flex justify-center w-full bg-white border-t border-solid"></div> -->
        </div>
        <div id="rightContainer" class="rightContainer"></div>
    </div>
</template>

<script setup>
import '../styles.css';
import sdk from "../application-ui-sdk/src/index";
const { formConfig, FormBuilder, formState } = sdk;
</script>
