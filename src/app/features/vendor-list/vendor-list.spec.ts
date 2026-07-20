import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VendorListComponent } from './vendor-list';

describe('VendorList', () => {
  let component: VendorListComponent;
  let fixture: ComponentFixture<VendorListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VendorListComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(VendorListComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
