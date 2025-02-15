<template>
	<div class="space-y-5">
		<Card :title="$t('balance')" :activeHeight="true">
			<div v-if="!$resources.upcomingInvoice.loading">
				<div class="mb-4 grid grid-cols-2 gap-4">
					<div class="flex flex-col gap-4">
						<div class="rounded-md border p-4">
							<div class="mb-2 flex justify-between text-base">
								<div>{{ $t('deposit_balance') }}</div>
							</div>
							<div class="text-2xl font-medium">
								{{ availableCredits }}
							</div>
						</div>
						<div class="rounded-md border p-4">
							<div class="mb-2 flex justify-between text-base">
								<div class="flex">
									<div class="mr-1">{{ $t('promotional_balance_1') }}</div>
									<Tooltip
										:text="
											$resources.upcomingInvoice.data?.val_check_promotion
												? `${$t('billingsummary_content_1')} ` +
												  this.$formatDate(
														$resources.upcomingInvoice.data?.date_promotion_1
												  )
												: $t('billingsummary_content_2')
										"
									>
										<FeatherIcon
											name="help-circle"
											class="ml-auto h-4 w-4 text-gray-700"
										/>
									</Tooltip>
								</div>
							</div>
							<div class="text-2xl font-medium">
								{{ khuyenMai1 }}
							</div>
						</div>
						<div class="rounded-md border p-4">
							<div class="mb-2 flex justify-between text-base">
								<div class="flex">
									<div class="mr-1">{{ $t('promotional_balance_2') }}</div>
									<Tooltip :text="$t('billingsummary_content_3')">
										<FeatherIcon
											name="help-circle"
											class="ml-auto h-4 w-4 text-gray-700"
										/>
									</Tooltip>
								</div>
							</div>
							<div class="text-2xl font-medium">
								{{ khuyenMai2 }}
							</div>
						</div>
					</div>
					<div class="flex flex-col gap-4">
						<div class="rounded-md border p-4">
							<div class="mb-2 text-base">
								{{ $t('this_month_provisional_invoice') }}
							</div>
							<div class="text-2xl font-medium">
								{{
									upcomingInvoice
										? this.$formatMoney(upcomingInvoice.total, 0) + ' VND'
										: '0 VND'
								}}
							</div>
						</div>
						<div class="rounded-md border p-4">
							<div class="mb-2 flex justify-between text-base">
								<div class="flex">
									<div class="mr-1">{{ $t('billingsummary_content_5') }}</div>
									<Tooltip :text="$t('billingsummary_content_6')">
										<FeatherIcon
											name="help-circle"
											class="ml-auto h-4 w-4 text-gray-700"
										/>
									</Tooltip>
								</div>
							</div>
							<div class="text-2xl font-medium">
								{{ soTienAI }}
							</div>
						</div>
						<div class="rounded-md border p-4">
							<div class="mb-2 flex justify-between text-base">
								<div>{{ $t('unpaid_invoice') }}</div>
							</div>
							<div class="text-2xl font-medium">{{ unpaidAmountDue }}</div>
						</div>
					</div>

					<div class="col-span-2 rounded-md border p-4">
						<div class="mb-5 border-b border-dashed pb-2">
							<div class="mb-2 flex justify-between text-base">
								<div>{{ $t('account_balance') }}</div>
							</div>
							<div class="text-2xl font-medium">
								{{
									this.$formatMoney(
										$resources.upcomingInvoice.data?.available_credits
											?.amount_all
									)
								}}
								VND
							</div>
						</div>
						<div class="mb-5 border-b border-dashed pb-2">
							<div class="mb-2 text-base">{{ $t('available_balance') }}</div>
							<div class="text-2xl font-medium">
								{{ availableBalances }}
							</div>
						</div>
						<div
							v-if="soTienThanhToan > 0"
							class="mb-3 flex flex-wrap justify-between text-base"
						>
							<div class="mb-2">
								{{ $t('top_up') }} {{ this.$formatMoney(soTienThanhToan) }} VND
								{{ $t('billingsummary_content_4') }}
							</div>
							<Button
								@click="showPrepaidCreditsDialog = true"
								theme="gray"
								iconLeft="credit-card"
								>{{ $t('payment') }}</Button
							>
						</div>
						<div v-else class="mb-3 flex flex-wrap justify-between text-base">
							<div class="mb-2">{{ $t('deposit_money_into_account') }}</div>
							<Button
								@click="showPrepaidCreditsDialog = true"
								theme="gray"
								iconLeft="plus"
								>{{ $t('deposit_money') }}</Button
							>
						</div>
					</div>
					<!-- <div class="rounded-md border p-4">
						<div class="flex justify-between text-base">
							<div>Phương thức thanh toán</div>
							<Button @click="showChangeModeDialog = true" theme="gray"
								>Thay đổi</Button
							>
						</div>
						<div class="text-2xl font-medium">
							{{
								$account.team.payment_mode == 'Prepaid Credits' ? 'Trả trước'
									: $account.team.payment_mode || 'Chưa đặt'
							}}
						</div>
					</div> -->
				</div>

				<!-- <a
					href="https://doc.mbwcloud.com/User_Guide_MBWCloud/lựa-chọn-thanh-toán"
					target="_blank"
					class="text-sm text-gray-700 underline"
				>
					Các phương thức thanh toán khác
				</a> -->
				<ErrorMessage
					:message="$resources.upcomingInvoice.error"
					class="mt-3"
				/>
			</div>

			<div class="py-20 text-center" v-if="loading">
				<Button :loading="true" :loadingText="$t('loading')" />
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
	props: ['checkRefresh'],
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
		}
		// unpaidAmountDue() {
		// 	return {
		// 		url: 'press.api.billing.total_unpaid_amount',
		// 		auto: true
		// 	};
		// }
	},
	watch: {
		checkRefresh: function () {
			this.$resources.upcomingInvoice.reload();
		}
	},
	data() {
		return {
			showPrepaidCreditsDialog: false,
			showChangeModeDialog: false
		};
	},
	mounted() {
		this.$socket.on('balance_updated', () => {
			setTimeout(() => {
				this.$resources.upcomingInvoice.reset();
				this.$resources.upcomingInvoice.reload();
			}, 1000);
		});

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
			const minimumDefault = 10000;
			let sotien =
				this.$resources.upcomingInvoice.data?.so_tien_goi_y_thanh_toan || 0;

			return sotien > minimumDefault ? sotien : minimumDefault;
		},
		upcomingInvoice() {
			return this.$resources.upcomingInvoice.data?.upcoming_invoice;
		},
		unpaidAmountDue() {
			return (
				this.$formatMoney(
					this.$resources.upcomingInvoice.data?.total_unpaid_amount
				) + ' VND'
			);
		},
		availableBalances() {
			let total = this.$resources.upcomingInvoice.data?.available_balances || 0;
			return this.$formatMoney(total, 0) + ' VND';
		},
		soTienThanhToan() {
			return this.$resources.upcomingInvoice.data?.so_tien_goi_y_thanh_toan;
		},
		availableCredits() {
			let amount =
				this.$resources.upcomingInvoice.data?.available_credits
					?.amount_available_credits;
			// if (this.$account.team.payment_mode === 'Partner Credits') {
			// 	amount = this.$resources.availablePartnerCredits.data;
			// }
			return this.$formatMoney(amount, 0) + ' VND';
		},
		khuyenMai1() {
			let amount =
				this.$resources.upcomingInvoice.data?.available_credits
					?.promotion_balance_1;
			return this.$formatMoney(amount, 0) + ' VND';
		},
		khuyenMai2() {
			let amount =
				this.$resources.upcomingInvoice.data?.available_credits
					?.promotion_balance_2;
			return this.$formatMoney(amount, 0) + ' VND';
		},
		soTienAI() {
			let amount =
				this.$resources.upcomingInvoice.data?.so_tien_dich_vu_ai_tam_tinh;
			return this.$formatMoney(amount, 0) + ' VND';
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
