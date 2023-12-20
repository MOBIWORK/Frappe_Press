<template>
	<div class="space-y-5">
		<Card title="Tóm lược thanh toán">
			<div v-if="!$resources.upcomingInvoice.loading">
				<div class="mb-4 grid grid-cols-2 gap-4">
					<div class="rounded-md border p-4">
						<div class="mb-2 text-base">Số tiền thanh toán hiện tại</div>
						<div class="text-2xl font-medium">
							{{ upcomingInvoice ? upcomingInvoice.formatted.total : '0 VND' }}
						</div>
					</div>
					<div class="rounded-md border p-4">
						<div class="flex justify-between text-base">
							<div>Tổng số tiền chưa thanh toán</div>
							<Button
								@click="showPrepaidCreditsDialog = true"
								theme="gray"
								iconLeft="credit-card"
								>Thanh toán</Button
							>
						</div>
						<div class="text-2xl font-medium">
							<!-- {{
								($account.team.currency == 'INR' ? '₹' : '$') +
								' ' +
								$resources.unpaidAmountDue.data
							}} -->
							{{
								$resources.unpaidAmountDue.data +
								' ' +
								($account.team.currency == 'VND' ? 'VND' : '$')
							}}
						</div>
					</div>
					<div class="rounded-md border p-4">
						<div class="flex justify-between text-base">
							<div>Số dư tài khoản</div>
							<Button
								@click="showPrepaidCreditsDialog = true"
								theme="gray"
								iconLeft="plus"
								>Thêm</Button
							>
						</div>
						<div class="text-2xl font-medium">
							{{ availableCredits }}
						</div>
					</div>

					<div class="rounded-md border p-4">
						<div class="flex justify-between text-base">
							<div>Phương thức thanh toán</div>
							<Button @click="showChangeModeDialog = true" theme="gray"
								>Thay đổi</Button
							>
						</div>
						<div class="text-2xl font-medium">
							{{
								$account.team.payment_mode == 'Prepaid Credits'
									? 'Tín dụng trả trước'
									: $account.team.payment_mode || 'Chưa đặt'
							}}
						</div>
					</div>
				</div>

				<a
					href="https://doc.mbwcloud.com/User_Guide_MBWCloud/lựa-chọn-thanh-toán"
					target="_blank"
					class="text-sm text-gray-700 underline"
				>
					Các phương thức thanh toán khác
				</a>
				<ErrorMessage
					:message="$resources.upcomingInvoice.error"
					class="mt-3"
				/>
			</div>

			<div class="py-20 text-center" v-if="loading">
				<Button :loading="true" loadingText="Đang tải" />
			</div>

			<ChangePaymentModeDialog v-model="showChangeModeDialog" />

			<PrepaidCreditsDialog
				v-if="showPrepaidCreditsDialog"
				v-model:show="showPrepaidCreditsDialog"
				:minimumAmount="Math.ceil(minimumAmount)"
				@success="
					() => {
						$resources.upcomingInvoice.reload();
						showPrepaidCreditsDialog = false;
					}
				"
			/>
		</Card>
		<UpcomingInvoiceSummary
			:invoice-doc="upcomingInvoice"
			v-if="upcomingInvoice?.items.length"
		/>
	</div>
</template>
<script>
import PlanIcon from '@/components/PlanIcon.vue';
import UpcomingInvoiceSummary from './UpcomingInvoiceSummary.vue';
import { defineAsyncComponent } from 'vue';
import InvoiceUsageTable from '@/components/InvoiceUsageTable.vue';

export default {
	name: 'BillingSummary',
	components: {
		InvoiceUsageTable,
		PlanIcon,
		UpcomingInvoiceSummary,
		PrepaidCreditsDialog: defineAsyncComponent(() =>
			import('@/components/PrepaidCreditsDialog.vue')
		),
		ChangePaymentModeDialog: defineAsyncComponent(() =>
			import('@/components/ChangePaymentModeDialog.vue')
		)
	},
	resources: {
		upcomingInvoice: { url: 'press.api.billing.upcoming_invoice', auto: true },
		availablePartnerCredits() {
			return {
				url: 'press.api.billing.get_partner_credits'
			};
		},
		unpaidAmountDue() {
			return {
				url: 'press.api.billing.total_unpaid_amount',
				auto: true
			};
		}
	},
	data() {
		return {
			showPrepaidCreditsDialog: false,
			showChangeModeDialog: false
		};
	},
	mounted() {
		this.$socket.on('balance_updated', () =>
			this.$resources.upcomingInvoice.reload()
		);

		if (this.$account.team.payment_mode === 'Partner Credits') {
			this.$resources.availablePartnerCredits.submit();
		}
	},
	unmounted() {
		this.$socket.off('balance_updated');
	},
	computed: {
		cardBrand() {
			return {
				'master-card': defineAsyncComponent(() =>
					import('@/components/icons/cards/MasterCard.vue')
				),
				visa: defineAsyncComponent(() =>
					import('@/components/icons/cards/Visa.vue')
				),
				amex: defineAsyncComponent(() =>
					import('@/components/icons/cards/Amex.vue')
				),
				jcb: defineAsyncComponent(() =>
					import('@/components/icons/cards/JCB.vue')
				),
				generic: defineAsyncComponent(() =>
					import('@/components/icons/cards/Generic.vue')
				),
				'union-pay': defineAsyncComponent(() =>
					import('@/components/icons/cards/UnionPay.vue')
				)
			};
		},
		minimumAmount() {
			const unpaidAmount = this.$resources.unpaidAmountDue.data;
			// const minimumDefault = $account.team.currency == 'INR' ? 800 : 10;
			const minimumDefault = 1000;

			return unpaidAmount && unpaidAmount > minimumDefault
				? unpaidAmount
				: minimumDefault;
		},
		upcomingInvoice() {
			return this.$resources.upcomingInvoice.data?.upcoming_invoice;
		},
		availableCredits() {
			if (this.$account.team.payment_mode === 'Partner Credits') {
				return this.$resources.availablePartnerCredits.data;
			}

			return this.$resources.upcomingInvoice.data?.available_credits;
		},
		paymentDate() {
			if (!this.upcomingInvoice) {
				return '';
			}
			let endDate = this.$date(this.upcomingInvoice.period_end);
			return endDate.toLocaleString({
				month: 'short',
				day: 'numeric',
				year: 'numeric'
			});
		},
		paymentModeDescription() {
			let payment_mode = this.$account.team.payment_mode;
			let balance = this.$account.balance;
			if (payment_mode === 'Card') {
				if (!this.upcomingInvoice || balance <= 0) {
					return `Thẻ của bạn sẽ được tính phí vào ${this.paymentDate}.`;
				} else if (balance >= this.upcomingInvoice.total) {
					return `Số dư tài khoản của bạn sẽ bị trừ vào ${this.paymentDate}.`;
				} else if (balance > 0) {
					return `Số dư tài khoản của bạn sẽ được trừ, sau đó số dư còn lại sẽ được tính từ thẻ của bạn vào ${this.paymentDate}.`;
				} else {
					return `Thẻ của bạn sẽ được tính phí vào ${this.paymentDate}.`;
				}
			}
			if (payment_mode === 'Prepaid Credits') {
				return `Bạn sẽ bị tính phí từ số dư tài khoản vào ${this.paymentDate}.`;
			}

			if (payment_mode === 'Partner Credits') {
				return `Bạn sẽ bị tính phí từ số dư đối tác của bạn vào ${this.paymentDate}.`;
			}
			return '';
		},
		loading() {
			return this.$resources.upcomingInvoice.loading;
		}
	},
	methods: {
		dateShort(date) {
			return this.$date(date).toLocaleString({
				month: 'short',
				day: 'numeric',
				year: 'numeric'
			});
		}
	}
};
</script>
