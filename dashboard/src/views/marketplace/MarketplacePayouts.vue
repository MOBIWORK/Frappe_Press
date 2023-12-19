<script setup>
import { createResource } from 'frappe-ui';
import MarketplacePayoutDetails from './MarketplacePayoutDetails.vue';

const props = defineProps({
	payoutOrderName: {
		type: String
	}
});

const payouts = createResource({
	url: 'press.api.marketplace.get_payouts_list',
	auto: true
});
</script>

<template>
	<Card
		v-if="!props.payoutOrderName"
		title="Tiền chi trả"
		subtitle="Xem những gì bạn đã kiếm được"
	>
		<Button v-if="payouts.loading" :loading="true">Đang tải</Button>

		<div v-else-if="payouts.data && payouts.data.length > 0">
			<div class="divide-y">
				<div
					class="grid grid-cols-4 items-center gap-x-8 py-4 text-base text-gray-600 md:grid-cols-6"
				>
					<span>Ngày đến hạn</span>
					<span class="hidden md:inline">Phương thức thanh toán</span>
					<span class="hidden md:inline">Trạng thái</span>
					<!-- <span>Net INR</span>
					<span>Net USD</span> -->
					<span>VND</span>
					<span></span>
				</div>

				<div
					v-for="payout in payouts.data"
					:key="payout.name"
					class="grid grid-cols-4 items-center gap-x-8 py-4 text-base text-gray-900 md:grid-cols-6"
				>
					<div v-if="payout.due_date">
						{{
							$date(payout.due_date).toLocaleString({
								month: 'long',
								day: 'numeric',
								year: 'numeric'
							})
						}}
					</div>
					<div v-else>Chưa đặt</div>

					<div class="hidden md:inline">
						{{ payout.mode_of_payment }}
					</div>

					<div class="hidden md:inline">
						<Badge :label="payout.status" />
					</div>

					<!-- <div>₹{{ round(payout.net_total_inr, 2) }}</div> -->

					<div>${{ round(payout.net_total_usd, 2) }}</div>

					<div>
						<Button :route="`/marketplace/payouts/${payout.name}`"
							>Xem chi tiết</Button
						>
					</div>
				</div>
			</div>
		</div>

		<div v-if="payouts.data && payouts.data.length == 0">
			<p class="my-3 text-center text-base text-gray-600">
				Bạn chưa có khoản tiền chi trả nào.
			</p>
		</div>
		<ErrorMessage :message="payouts.error" />
	</Card>
	<Card v-else title="Chi tiết tiền chi trả">
		<template #actions-left>
			<Button route="/marketplace/payouts"> ← Trở lại </Button>
		</template>
		<MarketplacePayoutDetails :payoutOrderName="payoutOrderName" />
	</Card>
</template>
