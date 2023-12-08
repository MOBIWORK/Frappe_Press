<script setup>
import { computed, ref, defineAsyncComponent } from 'vue';
import { utils } from '@/utils';
import { createResource } from 'frappe-ui';
import AlertSiteUpdate from '@/components/AlertSiteUpdate.vue';
import AlertSiteActivation from '@/components/AlertSiteActivation.vue';

const SitePlansDialog = defineAsyncComponent(() =>
	import('./SitePlansDialog.vue')
);
const BillingInformationDialog = defineAsyncComponent(() =>
	import('@/components/BillingInformationDialog.vue')
);

const props = defineProps({ site: Object, plan: Object });
const showPromotionalDialog = ref(false);
const clickedPromotion = ref(null);
const showBillingDialog = ref(false);
const showChangePlanDialog = ref(false);

const closeToLimits = computed(() => {
	if (!(props.site && props.plan)) return false;
	let usage = props.plan.usage_in_percent;
	return [usage.cpu, usage.database, usage.disk].some(x => 100 >= x && x > 80);
});

const limitExceeded = computed(() => {
	if (!(props.site && props.plan)) return false;
	let usage = props.plan.usage_in_percent;
	return [usage.cpu, usage.database, usage.disk].some(x => x > 100);
});

const isInTrial = computed(() => {
	return props.site?.trial_end_date;
});

const trialEndsText = computed(() => {
	if (!props.site?.trial_end_date) {
		return 0;
	}
	return utils.methods.trialEndsInDaysText(props.site.trial_end_date);
});

const siteMigrationText = computed(() => {
	const status = props.site?.site_migration.status;

	if (status === 'Running') {
		return 'Công việc di chuyển trang web của bạn đang trong quá trình tiến hành';
	} else if (status === 'Pending') {
		return 'Quá trình di chuyển trang web của bạn sẽ bắt đầu trong thời gian ngắn';
	} else if (status === 'Scheduled') {
		return `Quá trình di chuyển trang web của bạn đã được lên lịch để diễn ra ${utils.methods.formatDate(
			props.site?.site_migration.scheduled_time,
			'relative'
		)}.`;
	}
});

const siteVersionUpgradeText = computed(() => {
	const status = props.site?.version_upgrade.status;

	if (status === 'Running') {
		return 'Quá trình nâng cấp phiên bản trang web của bạn đang trong quá trình tiến hành';
	} else if (status === 'Pending') {
		return 'Quá trình nâng cấp phiên bản trang web của bạn sẽ bắt đầu trong thời gian ngắn';
	} else if (status === 'Scheduled') {
		return `Quá trình nâng cấp phiên bản trang web của bạn đã được lên lịch để diễn ra ${utils.methods.formatDate(
			props.site?.version_upgrade.scheduled_time,
			'relative'
		)}.`;
	}
});

const marketplacePromotionalBanners = createResource({
	url: 'press.api.marketplace.get_promotional_banners',
	auto: true
});
</script>

<template>
	<div class="space-y-2">
		<AlertSiteActivation :site="site" />
		<AlertSiteUpdate :site="site" />

		<div
			v-if="
				marketplacePromotionalBanners.data &&
				marketplacePromotionalBanners.data.length > 0
			"
		>
			<Alert
				v-for="banner in marketplacePromotionalBanners.data"
				:title="banner.alert_title"
				:key="banner.name"
			>
				{{ banner.alert_message }}

				<template #actions>
					<Button
						class="whitespace-nowrap"
						variant="solid"
						@click="
							() => {
								showPromotionalDialog = true;
								clickedPromotion = banner;
							}
						"
					>
						Xem thêm
					</Button>
				</template>
			</Alert>
		</div>
		<Alert title="Thử nghiệm" v-if="isInTrial && $account.hasBillingInfo">
			Thời gian thử nghiệm của bạn sẽ kết thúc vào {{ trialEndsText }}, sau đó
			trang web của bạn sẽ bị tạm ngừng. Thêm thông tin thanh toán của bạn để
			tránh tình trạng tạm ngừng.

			<template #actions>
				<Button
					class="whitespace-nowrap"
					@click="showBillingDialog = true"
					variant="solid"
				>
					Thêm thông tin thanh toán
				</Button>
			</template>
		</Alert>
		<Alert title="Thử nghiệm" v-if="isInTrial && $account.hasBillingInfo">
			Thời gian thử nghiệm của bạn sẽ kết thúc vào {{ trialEndsText }}, sau đó
			trang web của bạn sẽ bị tạm ngừng. Chọn một gói để tránh tình trạng tạm
			ngừng.

			<template #actions>
				<Button
					class="whitespace-nowrap"
					@click="showChangePlanDialog = true"
					variant="solid"
				>
					Chọn Gói
				</Button>
			</template>
		</Alert>
		<Alert title="Yêu cầu chú ý" v-if="limitExceeded">
			Trang web của bạn đã vượt quá sử dụng được phép cho gói của bạn. Nâng cấp
			gói ngay bây giờ.
		</Alert>
		<Alert title="Yêu cầu chú ý" v-else-if="closeToLimits">
			Trang web của bạn đã vượt quá 80% sử dụng được phép cho gói của bạn. Nâng
			cấp gói ngay bây giờ.
		</Alert>

		<Alert title="Di chuyển trang web" v-if="site?.site_migration">
			{{ siteMigrationText }}
			<template #actions>
				<Button
					v-if="
						site.site_migration.status === 'Running' &&
						site.site_migration.job_id
					"
					class="whitespace-nowrap"
					variant="solid"
					:route="{
						name: 'SiteJobs',
						params: { jobName: site.site_migration.job_id }
					}"
				>
					Xem Công việc
				</Button>
			</template>
		</Alert>

		<Alert title="Nâng cấp phiên bản" v-if="site?.version_upgrade">
			{{ siteVersionUpgradeText }}
			<template #actions>
				<Button
					v-if="
						site.version_upgrade.status === 'Running' &&
						site.version_upgrade.job_id
					"
					class="whitespace-nowrap"
					variant="solid"
					:route="{
						name: 'SiteJobs',
						params: { jobName: site.version_upgrade.job_id }
					}"
				>
					Xem Công việc
				</Button>
			</template>
		</Alert>

		<Dialog
			v-model="showPromotionalDialog"
			@close="e => (clickedPromotion = null)"
			:options="{
				title: 'MBW Cloud Marketplace',
				actions: [
					{
						variant: 'solid',
						route: `/install-app/${clickedPromotion?.app}`,
						label: 'Cài đặt ứng dụng'
					}
				]
			}"
		>
			<template #body-content>
				<div v-if="clickedPromotion" class="flex flex-row items-center">
					<Avatar
						class="mr-2"
						size="lg"
						shape="square"
						:image="clickedPromotion.image"
						:label="clickedPromotion.title"
					/>

					<div class="flex flex-col">
						<h4 class="text-xl font-semibold text-gray-900">
							{{ clickedPromotion.title }}
						</h4>
						<p class="text-base text-gray-600">
							{{ clickedPromotion.description }}
						</p>
					</div>
				</div>
			</template>
		</Dialog>

		<BillingInformationDialog
			v-model="showBillingDialog"
			v-if="showBillingDialog"
		/>

		<SitePlansDialog
			v-model="showChangePlanDialog"
			:site="site"
			:plan="plan"
			@plan-change="() => $emit('plan-change')"
		/>
	</div>
</template>
