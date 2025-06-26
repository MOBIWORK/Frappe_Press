<template>
    <div class="grid min-h-screen grid-cols-1 lg:grid-cols-2">
        <!-- Left Column: Background and Logo -->
        <div class="col-span-1 hidden h-screen bg-gray-50 lg:flex">
            <div v-if="saasProduct" class="relative h-screen w-full overflow-hidden bg-gradient-to-br from-blue-50 to-indigo-100">
                <!-- Background Image -->
                <img :src="saasProduct?.background" alt="Background" class="absolute inset-0 h-full w-full object-contain" />
                <!-- Logo on top -->
            </div>

            <div v-else class="relative h-screen w-full overflow-hidden bg-gradient-to-br from-blue-50 to-indigo-100">
                <!-- Background Image -->
                <img src="/public/bg1.png" alt="Background" class="absolute inset-0 h-full w-full object-contain" />
                <!-- Logo on top -->
                <div class="absolute left-8 top-8 z-10">
                    <MBWLogo class="h-16 w-auto drop-shadow-lg transition-all duration-300 hover:drop-shadow-xl" />
                </div>
            </div>
        </div>

        <!-- Right Column: Policy Form -->
        <div class="relative col-span-1 flex h-full w-full items-center justify-center py-3 px-3 md:py-6 md:px-6 lg:overflow-auto lg:bg-white overflow-hidden">
            <LoginBox 
                :title="__('Privacy Policy and Services')"
                class="w-full h-full lg:h-auto transition-all m-2 lg:m-5 xl:m-8 duration-300 shadow-xl rounded-xl max-w-full"
                customWidth="w-full max-w-none lg:max-w-[95%] xl:max-w-[90%] 2xl:max-w-[85%]"
            >
                <template v-slot:logo v-if="saasProduct">
                    <div class="flex mb-4 w-full justify-center">
                        <img 
                            class="h-12 md:h-16 w-auto rounded-md shadow-md transition-all duration-300 hover:shadow-lg" 
                            :src="saasProduct?.logo" 
                            alt="Product Logo" 
                        />
                    </div>
                </template>

                <div class="w-full">
                    <div class="w-full border rounded-md p-3 md:p-4 lg:p-5 xl:p-6 text-sm md:text-base">
                        <p class="font-semibold mb-2 lg:mb-3 text-sm md:text-base lg:text-lg xl:text-xl">
                            1. {{ __('Policy 1') }}
                        </p>
                        
                        <div class="h-32 md:h-40 lg:h-48 xl:h-56 overflow-y-auto border rounded p-2 md:p-3 lg:p-4 text-justify text-xs md:text-sm lg:text-base bg-white">
                            Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut
                            labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco
                            laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in
                            voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat
                            non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
                            <br><br>
                            Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, 
                            totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae 
                            dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, 
                            sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt.
                            <br><br>
                            Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, 
                            sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem.
                        </div>

                        <div class="flex items-center mt-3 lg:mt-4">
                            <Checkbox 
                                size="sm" 
                                :value="false" 
                                v-model="checkPolicy"
                                :label="__('I have read and agree to the above terms')" 
                                class="text-xs md:text-sm lg:text-base"
                            />
                        </div>

                        <button 
                            :disabled="!checkPolicy" 
                            @click="handleSubmit" 
                            :class="[
                                'w-full mt-3 lg:mt-4 py-2 md:py-2.5 lg:py-3 xl:py-4 rounded text-sm md:text-base lg:text-lg font-semibold transition-colors duration-200',
                                checkPolicy
                                    ? 'bg-red-600 hover:bg-red-700 text-white cursor-pointer transform hover:-translate-y-0.5'
                                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                            ]"
                        >
                            {{ __('Confirm') }}
                        </button>
                    </div>
                </div>

                <!-- Language Selector -->
                <template v-slot:footer>
                    <div class="flex items-center justify-center py-4 border-t border-gray-100 mt-6 w-full">
                        <SelectLanguage class="w-full opacity-80 hover:opacity-100 transition-opacity duration-300" />
                    </div>
                </template>
            </LoginBox>
        </div>
    </div>
</template>

<script>
import LoginBox from '../../components/auth/LoginBox.vue';
import SelectLanguage from '../../components/SelectLanguage.vue';
import { Checkbox } from 'frappe-ui'

export default {
    name: "SignupPolicy",
    props: ['productId'],
    components: {
        LoginBox,
        SelectLanguage
    },

    data() {
        return {
            checkPolicy: false
        };
    },
    resources: {
        saasProduct() {
            return {
                type: 'document',
                doctype: 'Product Trial',
                name: this.productId,
                auto: true,
            };
        },
        mySiteInfo() {
            return {
                url: 'press.api.site.is_check_user',
                params: {
                    email: localStorage.getItem('login_email'),
                },
                auto: true,
            };
        },
    },

    computed: {
        saasProduct() {
            return this.$resources.saasProduct?.doc;
        },
        selectedPlan() {
            try {
                // if (this.$route.query.selected_plan) {
                //     return JSON.parse(this.$route.query.selected_plan);
                // }
                const raw = this.$route.query.selected_plan;
                if (raw) {
                    const decoded = decodeURIComponent(raw);
                    return JSON.parse(decoded);
                }
            } catch (error) {
                console.error("Error parsing selected plan:", error);
            }
            return null;
        },
    },

    methods: {
        async handleSubmit() {
            if (!this.checkPolicy) return;
            if (!this.saasProduct) return;
            // Gọi API kiểm tra user/site/app
            const res = await this.$resources.mySiteInfo.fetch();
            const data = res && res.data ? res.data : res;
            let path = '/';
            const productId = this.saasProduct.name;
            // Nếu đã có site và chưa có app (productId) trong list_app
            if (data.site && !(data.list_app && data.list_app.includes(productId))) {
                path = `/create-site/${productId}/install-app-setup`;
            } else {
                // Nếu chưa có site hoặc đã có app thì vẫn đi flow cũ
                path = `/create-site/${productId}/setup`;
            }
            const encodedPlan = encodeURIComponent(JSON.stringify(this.selectedPlan));
            this.$router.push({
                path,
                query: {
                    selected_plan: encodedPlan
                },
            });
        }
    },

}
</script>