<template>
	<div class="min-h-screen bg-gray-50">
		<LoginBox>
			<h1 class="text-base text-gray-600">Quản lý đăng ký</h1>
			<div class="mt-4">
				<div class="text-xl font-medium text-gray-900">
					{{ site }}
				</div>
				<div
					class="mt-1 text-base text-gray-700"
					v-if="$resources.subscription.data?.trial_end_date"
				>
					Kết thúc dùng thử
					{{
						trialEndsInDaysText($resources.subscription.data?.trial_end_date)
					}}
				</div>
			</div>
			{{ success ? 'Bạn đã đăng ký gói' : '' }}
			<ErrorMessage class="mt-2" :message="$resources.subscription.error" />
			<div class="mt-8" v-if="$resources.subscription.data">
				<div>
					<button
						class="flex w-full items-center justify-between rounded-sm bg-gray-100 p-2 hover:bg-gray-200"
						@click="currentStep = 1"
					>
						<span class="text-sm font-medium text-gray-700">
							{{
								$resources.subscription.data.current_plan
									? 'Thay đổi gói'
									: 'Bước 1: Chọn gói'
							}}
						</span>
						<span
							class="text-sm font-bold text-gray-900"
							v-if="currentStep === 2"
						>
							{{ selectedPlan.plan_title
							}}<span class="font-normal">/tháng</span>
						</span>
					</button>
					<div class="mt-2 space-y-2" v-if="currentStep == 1">
						<button
							class="block w-full rounded border px-4 py-2.5 text-left"
							:class="[
								plan === selectedPlan
									? 'border-gray- outline outline-gray-900'
									: ''
							]"
							v-for="plan in $resources.subscription.data.plans"
							:key="plan.name"
							@click="selectedPlan = plan"
						>
							<div class="flex items-center justify-between">
								<div>
									<span class="text-base font-medium text-gray-900">
										{{ plan.plan_title }}
									</span>
									<span class="text-base text-gray-600">/tháng</span>
								</div>
								<Badge
									v-if="$resources.subscription.data.current_plan == plan.name"
								>
									Gói hiện tại
								</Badge>
								<CheckCircleIcon
									v-else-if="selectedPlan == plan"
									class="h-5 w-5"
								/>
							</div>
							<div class="mt-1 text-sm text-gray-600">
								<span>
									CPU {{ plan.cpu_time_per_day }}
									giờ/ngày
								</span>
								<span class="mx-1"> &middot; </span>
								<span>
									{{ formatBytes(plan.max_storage_usage, 0, 2) }} Database
								</span>
							</div>
						</button>
						<div class="flex justify-end">
							<Button
								v-if="!$resources.subscription.data.current_plan"
								variant="solid"
								@click="currentStep = 2"
							>
								Tiếp theo
							</Button>
							<Button
								v-else-if="
									selectedPlan?.name !==
									$resources.subscription.data.current_plan
								"
								variant="solid"
								:loading="$resources.setSubscriptionPlan.loading"
								@click="$resources.setSubscriptionPlan.submit()"
							>
								Thay đổi gói
							</Button>
						</div>
					</div>
				</div>
				<div class="mt-2" v-if="currentStep == 2">
					<div
						class="rounded-sm bg-gray-100 p-2 text-sm font-medium text-gray-700"
					>
						Bước 2: Thiết lập thanh toán
					</div>
					<StripeCard
						class="mt-4"
						@complete="$resources.setSubscriptionPlan.submit()"
					/>
				</div>
			</div>
		</LoginBox>
	</div>
</template>
<script>
import { defineAsyncComponent } from 'vue';
import { Badge, ErrorMessage, TextInput } from 'frappe-ui';
import LoginBox from '../partials/LoginBox.vue';
import CheckCircleIcon from '@/components/icons/CheckCircleIcon.vue';

export default {
	name: 'Subscription',
	props: ['site'],
	components: {
		LoginBox,
		Badge,
		TextInput,
		CheckCircleIcon,
		StripeCard: defineAsyncComponent(() =>
			import('@/components/StripeCard.vue')
		),
		ErrorMessage
	},
	data() {
		return {
			currentStep: 1,
			selectedPlan: null,
			success: false
		};
	},
	resources: {
		subscription() {
			return {
				url: 'press.api.saas.subscription',
				params: {
					site: this.site
				},
				auto: true,
				onSuccess(data) {
					if (data?.current_plan && data?.plans) {
						this.selectedPlan = data.plans.find(
							plan => plan.name === data.current_plan
						);
					}
				}
			};
		},
		setSubscriptionPlan() {
			return {
				url: 'press.api.saas.set_subscription_plan',
				params: {
					site: this.site,
					plan: this.selectedPlan?.name
				},
				onSuccess() {
					this.currentStep = 1;
					this.selectedPlan = null;
					this.$resources.subscription.reload();
				}
			};
		}
	}
};
</script>
