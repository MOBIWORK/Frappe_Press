<template>
	<div class="space-y-5">
		<Card title="Số dư" :activeHeight="true">
			<div v-if="!$resources.upcomingInvoice.loading">
				<div class="mb-4 grid grid-cols-2 gap-4">
					<div class="rounded-md border p-4">
						<div class="mb-2 flex justify-between text-base">
							<div>Số dư tiền nạp</div>
						</div>
						<div class="text-2xl font-medium">
							{{ availableCredits }}
						</div>
					</div>

					<div class="rounded-md border p-4">
						<div class="mb-2 text-base">Hóa đơn tạm tính tháng này</div>
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
								<div class="mr-1">Số dư khuyến mãi 1</div>
								<Tooltip
									:text="
										$resources.upcomingInvoice.data?.val_check_promotion
											? 'Khuyến mãi này được dùng đến hết ngày ' +
											  this.$formatDate(
													$resources.upcomingInvoice.data?.date_promotion_1
											  )
											: 'Đây là khuyến mãi số dư tài khoản có hạn sử dụng'
									"
								>
									<svg
										xmlns="http://www.w3.org/2000/svg"
										height="14"
										width="14"
										viewBox="0 0 512 512"
									>
										<path
											d="M464 256A208 208 0 1 0 48 256a208 208 0 1 0 416 0zM0 256a256 256 0 1 1 512 0A256 256 0 1 1 0 256zm169.8-90.7c7.9-22.3 29.1-37.3 52.8-37.3h58.3c34.9 0 63.1 28.3 63.1 63.1c0 22.6-12.1 43.5-31.7 54.8L280 264.4c-.2 13-10.9 23.6-24 23.6c-13.3 0-24-10.7-24-24V250.5c0-8.6 4.6-16.5 12.1-20.8l44.3-25.4c4.7-2.7 7.6-7.7 7.6-13.1c0-8.4-6.8-15.1-15.1-15.1H222.6c-3.4 0-6.4 2.1-7.5 5.3l-.4 1.2c-4.4 12.5-18.2 19-30.6 14.6s-19-18.2-14.6-30.6l.4-1.2zM224 352a32 32 0 1 1 64 0 32 32 0 1 1 -64 0z"
										/>
									</svg>
								</Tooltip>
							</div>
						</div>
						<div class="text-2xl font-medium">
							{{ khuyenMai1 }}
						</div>
					</div>

					<div class="rounded-md border p-4">
						<div class="mb-2 flex justify-between text-base">
							<div>Hóa đơn còn nợ</div>
						</div>
						<div class="text-2xl font-medium">
							{{ unpaidAmountDue }}
						</div>
					</div>

					<div class="rounded-md border p-4">
						<div class="mb-2 flex justify-between text-base">
							<div class="flex">
								<div class="mr-1">Số dư khuyến mãi 2</div>
								<Tooltip
									text="Đây là khuyến mãi số dư tài khoản có hạn sử dụng vĩnh viễn"
								>
									<svg
										xmlns="http://www.w3.org/2000/svg"
										height="14"
										width="14"
										viewBox="0 0 512 512"
									>
										<path
											d="M464 256A208 208 0 1 0 48 256a208 208 0 1 0 416 0zM0 256a256 256 0 1 1 512 0A256 256 0 1 1 0 256zm169.8-90.7c7.9-22.3 29.1-37.3 52.8-37.3h58.3c34.9 0 63.1 28.3 63.1 63.1c0 22.6-12.1 43.5-31.7 54.8L280 264.4c-.2 13-10.9 23.6-24 23.6c-13.3 0-24-10.7-24-24V250.5c0-8.6 4.6-16.5 12.1-20.8l44.3-25.4c4.7-2.7 7.6-7.7 7.6-13.1c0-8.4-6.8-15.1-15.1-15.1H222.6c-3.4 0-6.4 2.1-7.5 5.3l-.4 1.2c-4.4 12.5-18.2 19-30.6 14.6s-19-18.2-14.6-30.6l.4-1.2zM224 352a32 32 0 1 1 64 0 32 32 0 1 1 -64 0z"
										/>
									</svg>
								</Tooltip>
							</div>
						</div>
						<div class="text-2xl font-medium">
							{{ khuyenMai2 }}
						</div>
					</div>

					<div class="rounded-md border p-4">
						<div class="mb-2 text-base">Số dư khả dụng</div>
						<div class="text-2xl font-medium">
							{{ availableBalances }}
						</div>
					</div>

					<div class="col-span-2 rounded-md border p-4">
						<div class="mb-5">
							<div class="mb-2 flex justify-between text-base">
								<div>Số dư tài khoản</div>
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
						<div
							v-if="soTienThanhToan > 0"
							class="mb-3 flex flex-wrap justify-between text-base"
						>
							<div class="mb-2">
								Nạp thêm {{ this.$formatMoney(soTienThanhToan) }} VND để thanh
								toán hóa đơn nợ và hóa đơn đến cuối tháng
							</div>
							<Button
								@click="showPrepaidCreditsDialog = true"
								theme="gray"
								iconLeft="credit-card"
								>Thanh toán</Button
							>
						</div>
						<div v-else class="mb-3 flex flex-wrap justify-between text-base">
							<div class="mb-2">Nạp tiền vào tài khoản</div>
							<Button
								@click="showPrepaidCreditsDialog = true"
								theme="gray"
								iconLeft="plus"
								>Nạp tiền</Button
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
			const unpaidAmount =
				this.$resources.upcomingInvoice.data?.total_unpaid_amount;
			// const minimumDefault = $account.team.currency == 'INR' ? 800 : 10;
			let sotien =
				this.$resources.upcomingInvoice.data?.so_tien_goi_y_thanh_toan || 0;
			const minimumDefault = sotien || 2000;

			return unpaidAmount && unpaidAmount > minimumDefault
				? unpaidAmount
				: minimumDefault;
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
